
from django.conf import settings
from web.models import AppIdStore
import string
import random
from fabric import Connection
from hashlib import blake2b
from web.appid import generate_id,generate_password,get_salted_password

#email local part (string before @) has 64byte limit.
size = 20 # chars


def run(*args):

    def id_generator(size=size, chars=string.ascii_lowercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    existing_app_emails = AppIdStore.objects.all().values_list('app_email', flat=True)
    #existing_app_emails = ()
    count = 0

    #remote_shell = Connection("localhost")
    #command = "./Users/sandeep/Documents/SB_Sources/Kleeppr-django/mailserver/setup.sh list"
    command = "ls"

    while count < 5:
        #36^10 = 3,656,158,440,062,980 possible combinations # 3 trillion
        email = generate_id()
        if email in existing_app_emails:
            continue

        unsalted_password = generate_password()
        salted_password = get_salted_password(email,unsalted_password)
        #result = remote_shell.run(command)
        result = True
        if result:
            # insert to db
            print("success:",email,"@kleeppr.com","   unsalted_password:",unsalted_password,"    salted_password:",salted_password)
            d = AppIdStore.objects.create(app_id=email, app_id_secret=unsalted_password, assigned=False)
            d.save()
        else:
            print("failed:",email,"@kleeppr.com")

        count += 1

    for x in AppIdStore.objects.all():
        print(x.app_id, x.app_id_secret, x.assigned)