from django.conf import settings
from web.models import Feed,Publisher,Newsletters
from imapbox import Imapbox
from .parse_utils import parse_message_v2,insert_to_db


def run(*args):

    if (0):
        unverified_pubs = Publisher.objects.filter(is_verified=False)

        domains = ['washingtonpost.com']

        if domains:
            unverified_pubs = unverified_pubs.filter(domain__in=domains)

        for pub in unverified_pubs:
            print("#pub:",pub)
            # get feed, all uid
            # for each fetch message / parse / create appropriate newsletter record
            # update feed row with new newsletter id
            # boost confidence score of pub
            # manually fill in other info , update verified flag
            for nwl in Newsletters.objects.filter(publisher=pub.id):
                feed = Feed.objects.filter(nwl_id=nwl.id)
                for nwl in feed:
                    imapbox = Imapbox(settings.IMAP_HOST, settings.IMAP_USER,
                                      settings.IMAP_PASSWORD)

                    print("msg_id:",nwl.message_id)
                    message = imapbox.get_message_by_id(nwl.message_id)
                    nwl = parse_message_v2(nwl.message_id,message)
                    if nwl:
                        insert_to_db(nwl)


    else:
        imapbox = Imapbox(settings.IMAP_HOST, settings.IMAP_USER,
                                      settings.IMAP_PASSWORD)

        message = imapbox.get_message_by_id('28981')
        nwl = parse_message_v2('28981', message)
        print(nwl['body'])
        if nwl:
            insert_to_db(nwl)

