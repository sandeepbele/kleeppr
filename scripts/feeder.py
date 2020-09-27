import os, sys, argparse
from datetime import datetime
from imapbox import Imapbox
from django.conf import settings
from web.models import Feed,UserSettings, AppIdStore
from .parse_utils import parse_message, add_to_db, parse_message_v2, insert_to_db
import logging, pytz
from django.contrib.auth.models import User


def run(*args):

    logger = logging.getLogger("feeder")

    parser = argparse.ArgumentParser()
    parser.add_argument('--from_ts', default='2020-01-01 00:00:00',
                        help='timestamp to begin scraping from or upto depending on order')
    parser.add_argument('--limit', type=int, default=-1,
                        help='number of emails to fetch, default is all')

    args = parser.parse_args(args)

    lockfile = os.path.join('scrape_cron.lockfile')

    if os.path.exists(lockfile):
        logger.error("Lockfile exists. Is previous run finished? [...EXITING ]")
        sys.exit(0)

    logger.info("Starting run ...aquiring lock")
    try:

        open(lockfile,'a').close()

        for user in User.objects.filter(is_active=True,is_staff=False,is_superuser=False).all():
            user_settings = UserSettings.objects.filter(user_id=user.id).first()
            if not user_settings:
                logger.warn("Possible error situation: user settings not found for active user: %s", user.username)
                continue

            app_id_record = AppIdStore.objects.filter(app_id=user_settings.appid).first()
            if not app_id_record:
                logger.warn("Possible error situation: app_id record not found for active user: %s, appid:%s",
                            user.username, user_settings.appid)
                continue

            if 'from_ts' in args:
                last_fetched_ts = args.from_ts
            else:
                last_fetched_ts = "2020-01-01 00:00:00"  # datetime..strftime("%Y-%m-%d %H:%M:%S")

            last_fetched_ts = datetime.strptime(last_fetched_ts, "%Y-%m-%d %H:%M:%S")

            if user_settings.feeder_ts:
                last_fetched_ts = user_settings.feeder_ts

            if 'limit' in args:
                limit = args.limit
            else:
                limit = -1

            if limit < 0:
                logger.debug("Fetching all messages from: %s", str(last_fetched_ts))
            else:
                logger.debug("Fetching %d messages from: %s", limit, str(last_fetched_ts))

            imap_user = app_id_record.app_id
            imap_secret = app_id_record.app_id_secret

            try:
                imapbox = Imapbox(settings.IMAP_HOST, imap_user,
                                  imap_secret)

                count = 0
                for uid,message in imapbox.list_messages(last_fetched_ts, limit):
                    #print("uid:",uid)
                    nwl = parse_message_v2(uid,message)
                    if nwl:
                        insert_to_db(nwl,user_settings)
                        logger.debug("Message %s is parsed and added to Feed",str(uid))
                        count += 1

                if count > 0:
                    logger.info("[app_id:%s, from_ts:%s, limit: %d] Parsed and added %d records to Feed",
                                imap_user, last_fetched_ts, limit, count)
                    user_settings.feeder_ts = datetime.now(tz=pytz.UTC)
                    user_settings.save()

            except Exception as e:
                print(e)
                logger.error("Error in fetching or parsing messages: %s" % imap_user, e)

    except Exception as e:
        print(e)
        logger.error("Error in aquiring lock or getting last fetch time.", e)
        sys.exit(0)
    finally:
        logger.info("Run finished... lock is released")
        if os.path.exists(lockfile): # cleanup
            os.remove(lockfile)












