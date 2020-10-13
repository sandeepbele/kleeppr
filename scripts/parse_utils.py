
from django.conf import settings
from imapbox import Imapbox
import re, requests, tldextract
from pprint import pprint
from datetime import datetime
import pytz
from web.models import UserSettings,Feed,Newsletters,UserSubs,User,Publisher
from .rule_parser import process_rule, is_umbrella_publisher, is_publishing_platform
from bs4 import BeautifulSoup
from utils import MailUtils

def parse_message_v2(uid,email_message):

    nwl = dict()
    nwl['id'] = uid
    nwl['m_from'] = email_message.get("From")
    nwl['m_subject'] = email_message.get("Subject")
    nwl['m_unsub_header'] = email_message.get("List-Unsubscribe") or ""
    nwl['list_id'] = email_message.get("List-Id")

    is_mailing_list_msg = False

    for h in ('List-Unsubscribe','List-Id','X-Campaign','X-Rpcampaign','X-SES-Outgoing','Feedback-ID','Precedence'):
        if email_message.get(h):
            is_mailing_list_msg = True
            break;

    if not is_mailing_list_msg:
        print("[Rejected] not a mailing list message: From:%s, To:%s, MessageId:%s, Subject:%s"
              % (email_message.get("From"), email_message.get("To"), uid, email_message.get("Subject")))
        return None

    nwl['m_to'] = email_message.get("To")
    nwl['m_date'] = email_message.get("Date")

    m = re.search('([^<]+)\s*<([^@]+@([^>]+))>', nwl['m_from'])
    nwl_sender = m.group(1)
    nwl_email = m.group(2)
    nwl_domain = m.group(3)

    parsed_url = tldextract.extract(nwl_domain)
    #print(parsed_url.domain, parsed_url.suffix)
    parsed_domain = parsed_url.domain + "." + parsed_url.suffix

    nwl['sender'] = nwl_sender.strip()
    nwl['sender_email'] = nwl_email.strip()
    nwl['sender_email_domain'] = parsed_domain.strip()

    soup = BeautifulSoup(email_message.get_body().get_content(),'html.parser')
    nwl['body'] = soup.get_text()

    (letter, author) = process_rule(nwl)
    nwl['letter'] = letter
    nwl['author'] = author

    msg_body = email_message.get_body()

    # find unsubscribe link
    m = re.search('href="([^"]+unsubscribe[^"]+)"', str(msg_body))
    if m:
        nwl['unsub_link'] = m.group(1)
    else:
        m = re.search("(http.*?(unsub|disable).*?)>", nwl['m_unsub_header'])
        if m:
            nwl['unsub_link'] = m.group(1)
        else:
            nwl['unsub_link'] = "unknown"

    # shadow email
    #user_prefix = settings.IMAP_USER_PREFIX
    #m = re.search(user_prefix + '\+([^@]+)@', nwl['m_to'])
    #if m:
    #    nwl['appid'] = m.group(1)
    #elif nwl['m_to'].startswith('u'):
    #    nwl['appid'] = nwl['m_to'][:nwl['m_to'].index('@')]


    # formatted date
    ts = re.sub("\([A-Z]{3}\)", "", nwl['m_date'])
    ts = ts.strip()

    mailts = datetime.strptime(ts, "%a, %d %b %Y %H:%M:%S %z")
    mailts = mailts.astimezone(pytz.utc)
    nwl['ts'] = mailts.strftime("%Y-%m-%d %H:%M:%S%z")

    # is conformation email?
    is_confirmation = False
    #sub = email_message.get('Subject')
    if (re.search('(confirm|verify)\s+', nwl['m_subject'], re.I)
        or re.search('confirm', nwl['sender_email'], re.I)
        or re.search(
            'href="([^"]+confirm\W[^"]+)"', str(msg_body))) \
        or re.search('complete your signup',nwl['m_subject'],re.I)  \
        and not is_confirmation:

        is_confirmation = True

    nwl['possible_confirmation_email'] = is_confirmation

    txt_nodes = soup.find_all('p')
    txt = ""
    for txt_node in txt_nodes:
        txt += " " + txt_node.get_text().strip()
        if len(txt) > 600:
            break;

    if not txt:
        txt_nodes = soup.body.find_all(MailUtils.find_node_that_has_text)
        for txt_node in txt_nodes:
            txt += " " + txt_node.get_text().strip()
            if len(txt) > 600:
                break;

    if not txt:
        txt = soup.body.get_text()

    # print("-------------")
    # print(txt[:600])
    # print(txt)

    nwl['snippet'] = txt[:600]
    return nwl


def insert_to_db(nwl,user):

    # if list id?
    ## check if list_id in db
    ## yes - no?
    ### yes - get its id and add to feed against it
    ### no - create new publisher record, create default newsletter
    # elif letter?
    ## yes - no?
    ### yes - get its id and add to feed against it
    ## elif domain?
    ### yes - get its id and add to feed against it
    # else
    ## create publisher with domain and create newsletter with letter

    if is_umbrella_publisher(nwl['sender_email_domain']):
        dbnwl = Newsletters.objects.filter(letter=nwl['letter'])
    else:
        dbnwl = Newsletters.objects.filter(sender_email__icontains=nwl['sender_email_domain'])

    if dbnwl:
        dbnwl = dbnwl[0]
    else:
        if is_publishing_platform(nwl['sender_email_domain']):
            pub = Publisher.objects.filter(domain=nwl['sender_email'])
        elif is_umbrella_publisher(nwl['sender_email_domain']):
            pub = Publisher.objects.filter(domain=nwl['sender_email_domain'])
        else:
            pub = Publisher.objects.filter(name=nwl['author'], domain=nwl['sender_email_domain'])

        if pub:
            pub = pub[0]
        else:
            pub = Publisher.objects.create(name=nwl['author'], domain=nwl['sender_email_domain'])
            pub.save()
            print("[insert_to_db] created new pub:", pub)

        print("**",pub)
        dbnwl = Newsletters.objects.create(list_id=nwl['list_id'], letter=nwl['letter'], sender_email=nwl['sender_email'], url=nwl['sender_email_domain'], author=nwl['author'],
                                          publisher=pub)
        dbnwl.save()
        print("[insert_to_db] created new nwl[%d], name:%s, msg:%s, from:%s, sub:%s, pub:%d" % (dbnwl.id,dbnwl,nwl['id'],nwl['m_from'],nwl['m_subject'],pub.id))

    # add to usersub
    usersub = UserSubs.objects.filter(user_id=user.user_id).filter(nwl_id=dbnwl.id)

    if not usersub:
        usersub = UserSubs.objects.create(user_id=user.user_id,
                                     nwl_id=dbnwl,
                                     unsub_url=nwl['unsub_link'], feed_count=1)
        usersub.save()

    else:
        usersub = usersub[0]

    f = Feed.objects.filter(user_id=user.user_id, message_id=nwl['id']).first()

    # if feed row is present then update newsletter associated with it else create new row
    if f:
        if f.nwl_id != dbnwl:
            print("#updated feed row#",f.id," nwl_id from:",f.nwl_id," to:",dbnwl)
            f.nwl_id = dbnwl
            f.save()
            print("#check update:#",f.id," new nwl_id:",f.nwl_id)

        if f.intro is None:
            f.subject = nwl['m_subject']
            f.intro = nwl['snippet']

    else:
        is_confirmation_email = False
        if usersub.feed_count == 1 and nwl['possible_confirmation_email']:
            is_confirmation_email = True

        f = Feed.objects.create(user_id=user.user_id, message_id=nwl['id'], ts=nwl['ts'],
                                nwl_id=dbnwl,
                                is_confirmation=is_confirmation_email, subject=nwl['m_subject'],
                                intro=nwl['snippet'])
        f.save()

        usersub.feed_count += 1
        usersub.save()

def parse_message(uid,email_message):

    nwl = dict()

    nwl['id'] = uid
    nwl['body'] = email_message.get_body()
    msg_body = nwl['body']

    # parse headers
    nwl['m_to'] = email_message.get("To")
    nwl['m_from'] = email_message.get("From")
    nwl['m_subject'] = email_message.get("Subject")
    nwl['m_date'] = email_message.get("Date")
    nwl['m_unsub_header'] = email_message.get("List-Unsubscribe")
    nwl['m_list_id'] = email_message.get("List-Id")

    if not nwl['m_unsub_header']:
        print("rejected:not a mailing list message:",uid)
        return

    # Try to find newsletter home
    m = re.search('([^<]+)\s*<([^@]+@([^>]+))>', nwl['m_from'])
    nwl_sender = m.group(1)
    nwl_email = m.group(2)
    nwl_domain = m.group(3)

    nwl['sender_name'] = nwl_sender.strip()
    nwl['sender_email'] = nwl_email.strip()


    # try bunch of urls: keep one that succeeds
    urls = []
    # This is optional header/ substack has it
    hostname = email_message.get('List-Url')
    if hostname:
        m = re.match("<(.+)>",hostname)
        if m:
            hostname = m.group(1)
            urls.append(hostname)

    m = re.search("(http.*?)unsub",nwl['m_unsub_header'])
    if m:
        hostname = m.group(1)
        urls.append(hostname)

    parsed_url = tldextract.extract(nwl_domain)
    print(parsed_url.domain, parsed_url.suffix)
    parsed_domain = parsed_url.domain + "." + parsed_url.suffix

    urls.append("http://" + parsed_domain)
    urls.append("https://" + parsed_domain)
    urls.append("https://www." + parsed_domain)

    resp = None
    for p_url in urls:
        try:
            resp = requests.get(p_url, verify=False)
            print(p_url,resp.status_code)
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            print(e)

        if resp and resp.status_code == 200:
            break;

    url = "NA"
    if resp.status_code == 200:
        url = resp.request.url
        # special handling
        if "medium.com" in url:
            url = "NA"
            content = ""
        else:
            content = resp.content.decode("utf-8")

    else:
        # ERROR
        content = str(msg_body)
        url = 'NA'

    m = re.search('og:title"\s+content="([^"]+)"', content)
    if m:
        title = m.group(1)
    else:
        m = re.search('<title.*?>([^<>]+)<', content)
        if m:
            title = m.group(1)
        else:
            title = "unknown"

    m = re.search('og:description"\s+content="([^"]+)"', content)
    if m:
        desc = m.group(1)
    else:
        m = re.search('description"\s+content="([^"]+)"', content)
        if m:
            desc = m.group(1)
        else:
            desc = "unknown"

    m = re.search('og:url"\s+content="([^"]+)/?"', content)
    if m:
        url = m.group(1)

    m = re.search('genre"\s+content="([^"]+)"', content)
    if m:
        tags = m.group(1)
    else:
        tags = ""

    nwl['title'] = title
    nwl['desc'] = desc
    nwl['url'] = url
    nwl['tags'] = tags

    # find unsubscribe link
    m = re.search('href="([^"]+unsubscribe[^"]+)"', str(msg_body))
    if m:
        nwl['unsub_link'] = m.group(1)
    else :
        m = re.search("(http.*?(unsub|disable).*?)>", nwl['m_unsub_header'])
        if m:
            nwl['unsub_link'] = m.group(1)
        else:
            nwl['unsub_link'] = "unknown"

    # shadow email
    user_prefix = settings.IMAP_USER_PREFIX
    m = re.search(user_prefix + '\+([^@]+)@', nwl['m_to'])
    if m:
        nwl['appid'] = m.group(1)

    # formatted date
    ts = re.sub("\([A-Z]{3}\)", "", nwl['m_date'])
    ts = ts.strip()

    mailts = datetime.strptime(ts, "%a, %d %b %Y %H:%M:%S %z")
    mailts = mailts.astimezone(pytz.utc)
    nwl['ts'] = mailts.strftime("%Y-%m-%d %H:%M:%S%z")

    # is conformation email?
    is_confirmation = False
    sub = email_message.get('Subject')
    if (re.search('confirm|verify', nwl['m_subject'], re.I) or re.search('confirm', nwl['sender_email'], re.I) or re.search(
            'href="([^"]+confirm\W[^"]+)"', str(msg_body))) and not is_confirmation:
        is_confirmation = True
    nwl['is_confirmation'] = is_confirmation

    pprint(nwl)

    return nwl


def get_domain(url):
    parsed_url = tldextract.extract(url)
    print(parsed_url.domain, parsed_url.suffix)
    parsed_domain = parsed_url.domain + "." + parsed_url.suffix
    return parsed_domain


def add_to_db(nwl):

    # already has it?
    #message = Feed.objects.filter(message_id=nwl['id'])
    #if message:


    #    print("ERROR")
    #    return

    # associate user
    user = None
    if 'appid' in nwl:
        user = UserSettings.objects.filter(appid__exact=nwl['appid'])

    if not user:
        user = UserSettings.objects.filter(user_id=User.objects.filter(username='admin@kleeppr.com').get())

    if user:
        user = user[0]
    else:
        print("Error")
        return

    # check against sender list
    matched_nwls = Newsletters.objects.filter(sender_email=nwl['sender_email'])
    if not matched_nwls:
        matched_nwls = Newsletters.objects.filter(author=nwl['sender_name'])
    if not matched_nwls:
        get_domain()
    # if not check against sender name
    # if not match against sender domain

    # associate preexisting nwl record
    matched_nwls = Newsletters.objects.filter(sender_email=nwl['sender_email']).filter(author=nwl['sender_name'])
    if matched_nwls:
        nwl_rec = matched_nwls[0]
    else:
        nwl_rec = Newsletters.objects.create(letter=nwl['title'], sender_email=nwl['sender_email'], url=nwl['url'], desc=nwl['desc'], author=nwl['sender_name'],
                                         author_url=nwl['url'], extra_info=nwl['tags'])
        nwl_rec.save()

    # add to usersub
    usersub = UserSubs.objects.filter(user_id=user.user_id).filter(nwl_id=nwl_rec.id)

    if not usersub:
        us = UserSubs.objects.create(user_id=user.user_id,
                                     nwl_id=nwl_rec,
                                     unsub_url=nwl['unsub_link'], feed_count=1)
        us.save()

    else:
        usersub = usersub[0]
        usersub.feed_count += 1
        usersub.save()

    # add to feed
    f = Feed.objects.create(user_id=user.user_id,message_id=nwl['id'],ts=nwl['ts'],
                            nwl_id=nwl_rec,
                            is_confirmation=nwl['is_confirmation'])
    f.save()


def run(*args):
    '''
    #message_id = "27510" # substack
    #message_id = "26912" # gmail #ed yong #tinyletter
    #message_id = "27283" #sendgrid via gmail #epsilon theory# url travelrsal fails
                # try https #unsubscribe didnt match as its not in href but plain text
    message_id = "27245" #email domain goes to medium-non functional .. actual url is in email #mailchimp
    message_id = "27455" # zapier #product newsletter
    message_id = "27556"
    imapbox = Imapbox(settings.IMAP_HOST, settings.IMAP_USER,
                      settings.IMAP_PASSWORD)

    message = imapbox.get_message_by_id(message_id)
    print(message)
    #parse_message(message_id,message)

'''
    #message_ids = ["27510","26912","27283","27245","27455","27556","27473"]
    message_ids = ["28850"]

    for msg_id in message_ids:
        imapbox = Imapbox(settings.IMAP_HOST, settings.IMAP_USER,
                          settings.IMAP_PASSWORD)

        message = imapbox.get_message_by_id(msg_id)
        print(message)
        parse_message(msg_id,message)


