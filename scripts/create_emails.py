
from django.conf import settings
from web.models import AppIdStore
import string
import random
from fabric import Connection

from hashlib import blake2b
from web.appid import generate_id,generate_password,get_salted_password
import os


#email local part (string before @) has 64byte limit.
def run(*args):

    DRY_RUN = True

    existing_app_emails = AppIdStore.objects.all().values_list('app_id', flat=True)
    count = 0
    try:
        remote_shell = Connection(os.getenv('REMOTE_MAIL_SERVER'),user=os.getenv('REMOTE_MAIL_SERVER_SSH_USER'))
        remote_shell.connect_kwargs.password = os.getenv('REMOTE_MAIL_SERVER_SSH_PASSWORD')

        for x in range(1,5):
            #36^10 = 3,656,158,440,062,980 possible combinations # 3 trillion
            email = generate_id()
            #email = "u+demo"
            if email not in existing_app_emails:
                imap_username = email + "@" + os.getenv("APPID_MAIL_SERVER_DOMAIN")
                unsalted_password = generate_password()
                salted_password = get_salted_password(email,unsalted_password)

                if DRY_RUN:
                    add_account_cmd = "sh setup.sh email list"
                    add_restrictions_cmd = "sh setup.sh email restrict list send"
                else:
                    add_account_cmd = "sh setup.sh email add %s %s" % (imap_username,salted_password)
                    add_restrictions_cmd = "sh setup.sh email restrict list send %s" % imap_username

                with remote_shell.cd(os.getenv("REMOTE_MAIL_SERVER_WORKDIR")):
                    result = remote_shell.run(add_account_cmd,pty=True)
                    if result.ok:
                        # insert to db
                        result = remote_shell.run(add_restrictions_cmd,pty=True)
                        if not result.ok:
                            print("failed to add restriction",email,result)
                        if not DRY_RUN:
                            d = AppIdStore.objects.create(app_id=email, app_id_secret=unsalted_password, assigned=False)
                            d.save()
                        print("###success:", imap_username, "   unsalted_password:", unsalted_password,
                              "    salted_password:", salted_password)
                    else:
                        print("###failed:",email,"@kleeppr.com",result)

                count += 1

        print("created %d app ids" % count)
    finally:
        remote_shell.close()
    #for x in AppIdStore.objects.all():
    #    print(x.app_id, x.app_id_secret, x.assigned)