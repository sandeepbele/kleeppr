from django.db import connections
from django.test import TestCase, Client, RequestFactory, TransactionTestCase
from django.urls import reverse
from . import views
import threading, random, string
from django.contrib.auth.models import User
from .models import UserSubs,AppIdStore,UserSettings


def test_concurrently(times):


    """
    Add this decorator to small pieces of code that you want to test
    concurrently to make sure they don't raise exceptions when run at the
    same time.  E.g., some Django views that do a SELECT and then a subsequent
    INSERT might fail when the INSERT assumes that the data has not changed
    since the SELECT.
    """
    def test_concurrently_decorator(test_func):
        def wrapper(*args, **kwargs):
            exceptions = []
            def call_test_func():
                try:
                    test_func(*args, **kwargs)
                except Exception as e:
                    exceptions.append(e)
                    raise
            threads = []
            for i in range(times):
                threads.append(threading.Thread(target=call_test_func))
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            if exceptions:
                raise Exception('test_concurrently intercepted %s exceptions: %s' % (len(exceptions), exceptions))
        return wrapper
    return test_concurrently_decorator

# Create your tests here.
class RegisterUserTests(TransactionTestCase):

    number_available_emails = 35

    def setUp(self):
        print("setup")
        for x in range(0,self.number_available_emails):
            a = AppIdStore.objects.create(app_id=''.join(random.choices(string.ascii_letters, k=5)),
                                          app_id_secret='4e335c50fa8ca5273b9b1e4fc3b221ee11434b65')
            a.save()

        for a in AppIdStore.objects.all():
            print("###", a.app_id)

    def test_multithreadedUserCreation(self):
        self.multithreadedUserCreation()

        for a in UserSettings.objects.all():
            print("***", a.user_id,a.appid)

        self.assertGreaterEqual(len(User.objects.all()), self.number_available_emails)
        self.assertEqual(len(AppIdStore.objects.filter(assigned=True).all()), self.number_available_emails)
        self.assertEqual(len(UserSettings.objects.all()),self.number_available_emails)
        self.assertEqual(len(UserSettings.objects.values('appid').distinct()), self.number_available_emails)

    @test_concurrently(90)
    def multithreadedUserCreation(self):
        try:
            c = Client(enforce_csrf_checks=False)
            #c.login(username='user@example.com', password='abc123')
            rf = RequestFactory()
            url = reverse(views.register_user)
            username = ''.join(random.choices(string.ascii_letters,k=5))
            password1 = ''.join(random.choices(string.ascii_letters,k=10))
            #request = rf.post( url,{'username':'test_'+username+'@kleeppr.com','password1':password1})
            #response = views.register_user(request)
            response = c.post(url,{'username':'test_'+username+'@kleeppr.com','password1':password1,'password2':password1})
        finally:
            for con in connections.all():
                con.close()

        #self.assertEqual(response.status_code,200)
