import os, sys, argparse
from datetime import datetime
from imapbox import Imapbox
from django.conf import settings
from web.models import Feed
from .parse_utils import parse_message, add_to_db
import logging


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
        try:
            open(lockfile,'a').close()
            fd = Feed.objects.order_by('-ts')[:1]
        except Exception as e:
            print(e)
            logger.error("Error in aquiring lock or getting last fetch time.", e)
            sys.exit(0)

        if 'from_ts' in args:
            last_fetched_ts = args.from_ts
        else:
            last_fetched_ts = "2020-01-01 00:00:00"  # datetime..strftime("%Y-%m-%d %H:%M:%S")

        last_fetched_ts = datetime.strptime(last_fetched_ts, "%Y-%m-%d %H:%M:%S")

        if fd:
            fd = fd[0]
            last_fetched_ts = fd.ts

        if 'limit' in args:
            limit = args.limit
        else:
            limit = -1

        if limit < 0:
            logger.info("Fetching all messages from: %s", str(last_fetched_ts))
        else:
            logger.info("Fetching %d messages from: %s", limit, str(last_fetched_ts))

        try:
            imapbox = Imapbox(settings.IMAP_HOST, settings.IMAP_USER,
                              settings.IMAP_PASSWORD)

            count = 0
            for uid,message in imapbox.list_messages(last_fetched_ts, limit):
                nwl = parse_message(uid,message)
                add_to_db(nwl)
                logger.debug("Message %s is parsed and added to Feed",str(uid))
                count += 1

            logger.info("Parsed and added %d records to Feed",count)

        except Exception as e:
            print(e)
            logger.error("Error in fetching or parsing messages", e)
    finally:
        logger.info("Run finished... lock is released")
        if os.path.exists(lockfile): # cleanup
            os.remove(lockfile)












