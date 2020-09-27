from datetime import datetime
from imapbox import Imapbox
from django.conf import settings
import json, re
from .rule_parser import process_rule

try:
    imapbox = Imapbox(settings.IMAP_HOST, settings.IMAP_USER,
                      settings.IMAP_PASSWORD)

    stats = dict()

    count = 0
    last_fetched_ts = "2020-09-01 00:00:00"  # datetime..strftime("%Y-%m-%d %H:%M:%S")
    last_fetched_ts = datetime.strptime(last_fetched_ts, "%Y-%m-%d %H:%M:%S")
    limit = 5000
    for uid, message in imapbox.list_messages(last_fetched_ts, limit):
        #nwl = parse_message(uid, message)
        count += 1
        list_id = None
        for h in ('List-Id'):
            list_id = message.get(h)
            if list_id:
                break

        if not list_id:
            #list_id = message.get("From")

            # Try to find newsletter home
            m = re.search('([^<]+)\s*<([^@]+@([^>]+))>', message.get("From"))
            nwl_sender = m.group(1)
            nwl_email = m.group(2)

            sub = message.get("Subject")
            (letter,author) = process_rule({'m_subject':sub,
                                            'm_sender':nwl_sender,
                                            'm_sender_email':nwl_email}
                                           )
            list_id = letter

        nwl_stats = stats.get(list_id)
        if not nwl_stats:
            nwl_stats = dict()
            nwl_stats['senders'] = []
            nwl_stats['subjects'] = []
            nwl_stats['ids'] = []
            nwl_stats['authors'] = []
            stats[list_id] = nwl_stats

        if message.get("From") not in nwl_stats['senders']:
            nwl_stats['senders'].append(message.get("From"))

        if message.get("Subject") not in nwl_stats['subjects']:
            nwl_stats['subjects'].append(message.get("Subject"))

        if uid not in nwl_stats['ids']:
            nwl_stats['ids'].append(uid)

        if author not in nwl_stats['authors']:
            nwl_stats['authors'].append(author)

        print(count)

    with open("/Users/sandeep/Documents/SB_Sources/Kleeppr-django/kleeppr4/scripts/header_stats.json","w") as fp:
        json.dump(stats,fp, sort_keys=False,
                         indent=4, separators=(',', ': '))


except Exception as e:
    print(e)