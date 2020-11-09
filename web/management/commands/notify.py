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
from web.models import UserSettings

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
            parser.add_argument('--test_user',
                                help='Minutes since sign-up. Default 60.',
                                default=None)
            '''parser.add_argument('--notify',
                        action="store_true",
                        dest="notify",
                        help='Notify admins with new user information. Default False.',
                        default=False)'''
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
        test_user = options.get('test_user')
        dry = bool(options.get('dry'))
        verbose = bool(options.get('verbose'))
        notify = bool(options.get('notify'))
        welcome = bool(options.get('welcome'))
        email_verification = bool(options.get('email_verification'))

        t_user = None
        if test:
            if test_user is not None:
                t_user = UserSettings.objects.filter(user_id__username=test_user).first()
                print(t_user)
            else:
                print("test user does not exist")
                return

        if email_verification:
            users = UserSettings.objects.filter(email_verification_sent=False).filter(email_verified=False)
            template = "email/confirm_email.tpl"

            if test:
                users = [t_user]

            #print(users)

            for user in users:
                auth_user = User.objects.filter(pk=user.user_id.id).first()
                if not auth_user.is_active:
                    continue;

                url = '%s/activate_account/%s/%s' % (
                settings.MAIL_TEMPLATED_DOMAIN, urlsafe_base64_encode(bytes(str(auth_user.id), 'utf-8')),
                account_activation_token.make_token(auth_user))

                if not dry:
                    try:

                        send_mail(template,
                                  {'user': user, 'url': url},
                                  from_email=settings.WELCOME_FROM_EMAIL,
                                  recipient_list=[auth_user.email],
                                  fail_silently=False,
                                  auth_user=settings.EMAIL_HOST_USER,
                                  auth_password=settings.EMAIL_HOST_PASSWORD
                                  )
                        print("sending verification email to:",auth_user.email)

                        if not test:
                            user.email_verification_sent = True
                            user.save()

                    except Exception as e:
                        print(e)
                else:
                    print("[dry_run] sending verification email to:", auth_user.email)

        elif welcome:
            users = UserSettings.objects.filter(welcome_email_sent=False).filter(email_verified=True)
            template = "email/welcome.tpl"
            url = '%s%s' % (settings.MAIL_TEMPLATED_DOMAIN, reverse('index'))

            if test:
                users = [t_user]

            #print(users)

            for user in users:
                auth_user = User.objects.filter(pk=user.user_id.id).first()
                if not auth_user.is_active:
                    continue;

                if not dry:
                    try:
                        send_mail(template,
                                  {'user': user, 'url': url},
                                  from_email=settings.WELCOME_FROM_EMAIL,
                                  recipient_list=[auth_user.email],
                                  fail_silently=False,
                                  auth_user=settings.EMAIL_HOST_USER,
                                  auth_password=settings.EMAIL_HOST_PASSWORD
                                  )
                        print("sending welcome email to:", auth_user.email)
                        if not test:
                            user.welcome_email_sent = True
                            user.welcome_email_sent_at = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
                            user.save()

                    except Exception as e:
                        print(e)
                else:
                    print("[dry_run] sending welcome email to:", auth_user.email)

        else:
            print("invalid option")
            return
        '''
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
        '''