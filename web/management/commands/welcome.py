from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from mail_templated import send_mail
from optparse import make_option
import datetime,pytz
from django.urls import reverse
import uuid
from web.tokens import account_activation_token
from django.utils.http import urlsafe_base64_encode

class Command(BaseCommand):
    """
    Find users who have signed up in the past X minutes and email them.

    """

    def add_arguments(self, parser):

            parser.add_argument('--since',
                        help='Minutes since sign-up. Default 60.',
                        default=60)
            parser.add_argument('--test',
                        action="store_true",
                        dest="test",
                        help='Test run (emails user 0). Default False.',
                        default=False)
            parser.add_argument('--notify',
                        action="store_true",
                        dest="notify",
                        help='Notify admins with new user information. Default False.',
                        default=False)
            parser.add_argument('--dry',
                        action="store_true",
                        dest="dry",
                        help='Dry run, does not actually send emails. Default False.',
                        default=False)
            parser.add_argument('--quiet',
                        action="store_false",
                        dest="verbose",
                        help='Quiet emails being sent. Default False.',
                        default=True)
            parser.add_argument('--welcome',
                                action="store_true",
                                dest="welcome",
                                help='Send welcome email.',
                                default=False)

            parser.add_argument('--email_verification',
                        action="store_true",
                        dest="email_verification",
                        help='Send verification email.',
                        default=False)



    help = '''Find users who have signed up within the past X minutes (default 60) and email them.

Define your email templates in **TEMPALTE_DIR**/email/welcome.tpl and **TEMPALTE_DIR**/email/notify.tpl

You must also define your WELCOME_FROM_EMAIL and NOTIFICATION_TO_EMAIL in your settings file.

EXAMPLE:

/manage.py welcome --since 60'''

    def handle(self, **options):
        minutes = int(options.get('since'))
        test = bool(options.get('test'))
        dry = bool(options.get('dry'))
        verbose = bool(options.get('verbose'))
        notify = bool(options.get('notify'))
        welcome = bool(options.get('welcome'))
        email_verification = bool(options.get('email_verification'))

        # Get New Users
        today = datetime.datetime.now(pytz.UTC)
        minutes = datetime.timedelta(minutes=minutes)
        begin = today - minutes
        if not test:
            new_users = User.objects.filter(date_joined__range=(begin, today)).order_by('-date_joined')
        else:
            new_users = User.objects.all().order_by('date_joined')
            new_users = [new_users[0]]

        for user in new_users:

            if verbose:
                print("Welcoming " + str(user.username) + ' (' + str(user.email) + ').')

            if not dry:
                if welcome:
                    template = "email/welcome.tpl"
                    url = '%s%s' % (settings.MAIL_TEMPLATED_DOMAIN, reverse('index'))
                elif email_verification:
                    template = "email/confirm_email.tpl"
                    url = '%s/activate_account/%s/%s' % (
                    "http://localhost:8000", urlsafe_base64_encode(bytes(str(user.pk),'utf-8')), account_activation_token.make_token(user))
                else:
                    print("invalid option")
                    return
                    #url = '%s/activate_account/%s/%s' % (settings.MAIL_TEMPLATED_DOMAIN,uuid.uuid1().int>>64, account_activation_token.make_token(user) )

                try:
                    send_mail(template,
                              {'user': user,'url': url },
                              from_email=settings.WELCOME_FROM_EMAIL,
                              recipient_list=[user.email],
                              fail_silently=False,
                              auth_user=settings.EMAIL_HOST_USER,
                              auth_password=settings.EMAIL_HOST_PASSWORD
                              )
                except Exception as e:
                    print(e)

        if notify:

            num_new_users = str(len(new_users))

            if verbose:
                print(
                    'Sending notification of ' + num_new_users + ' new users to ' + settings.NOTIFICATION_TO_EMAIL + '.')

            if not dry:
                try:
                    send_mail("email/notify.tpl",
                              {'num_new_users': num_new_users, 'new_users': new_users},
                              from_email=settings.WELCOME_FROM_EMAIL,
                              recipient_list=[settings.NOTIFICATION_TO_EMAIL],
                              fail_silently=False,
                              auth_user=settings.EMAIL_HOST_USER,
                              auth_password=settings.EMAIL_HOST_PASSWORD
                              )
                except Exception as e:
                    print(e)
