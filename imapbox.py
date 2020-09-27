
import email,ssl,sys
from datetime import date

from imapclient import IMAPClient
from pprint import pprint
from email import policy
import mailcache
from web.appid import get_salted_password
from django.conf import settings
#HOST = "imap.gmail.com"
#USERNAME = "helloclipit"
#PASSWORD = "ttybhgxahhkealfa"


class Imapbox:

    def __init__(self,_host,_username,_password):
        self.HOST = _host
        self.USERNAME = _username

        if _username.startswith("u+"):
            self.USERNAME = "u"
            self.PASSWORD = settings.IMAP_PASSWORD
        else:
            self.PASSWORD = get_salted_password(_username,_password)

        self.USERNAME = self.USERNAME + "@kleeppr.com"

        self.ssl_context = ssl.create_default_context()
        # don't check if certificate hostname doesn't match target hostname
        self.ssl_context.check_hostname = False
        # don't check if the certificate is trusted by a certificate authority
        self.ssl_context.verify_mode = ssl.CERT_NONE

    def _get_credentials(self):
       pass

    def sync_messages(self,historyId=1, userId='me'):
        pass

    def list_messages(self,since_ts,limit):
        with IMAPClient(self.HOST, ssl_context=self.ssl_context) as server:
            server.login(self.USERNAME, self.PASSWORD)
            server.select_folder('INBOX', readonly=True)
            #messages = server.search(['UNSEEN', 'SINCE', since_ts])
            messages = server.sort(['REVERSE','DATE'],['UNSEEN', 'SINCE', since_ts])
            i=0;
            step=10;

            # limit = -1 which is default means fetch all
            if limit < 0:
                limit = len(messages)

            while i <= limit:
                msg_chunk = messages[i:i+step]
                print(msg_chunk)
                for uid, message_data in server.fetch(msg_chunk, 'RFC822').items():
                    # for uid, message_data in server.fetch(messages).items():
                    email_message = email.message_from_bytes(message_data[b'RFC822'], policy=policy.default)
                    #print(uid, email_message.get('From'), email_message.get('Subject'))
                    #pprint(email_message.items())
                    #print(email_message.get_body())
                    #sys.exit(1)
                    yield((uid,email_message))

                i += step

    # worst case : not implemented
    def pull_all(self):
        pass

    def get_messages_by_criteria(self, userId='me', criteria='*', maxResults=10, pageToken=None):
       pass

    def get_message_by_id(self, id):

        em = mailcache.get_from_cache(id)
        if not em:
            with IMAPClient(self.HOST, ssl_context=self.ssl_context) as server:
                server.login(self.USERNAME, self.PASSWORD)
                server.select_folder('INBOX', readonly=True)
                for uid, message_data in server.fetch(id, 'RFC822').items():
                    em = email.message_from_bytes(message_data[b'RFC822'], policy=policy.default)
                    mailcache.add_to_cache(uid,em)
        # pprint.pprint(email)
        # parse_message(email['payload'])
        return em

    def get_labels(self):
        pass