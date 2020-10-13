from django.db import transaction
from django.db.models import Q
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView
# Create your views here
from django.http import HttpResponse
from django.views.decorators.clickjacking import xframe_options_exempt
import django.contrib.auth.urls

from .models import UserSettings,User,Feed, Newsletters,UserSubs, Tags,AppIdStore
from hashlib import blake2b
from django.core.paginator import Paginator
from imapbox import Imapbox
from django.conf import settings
from pprint import pprint
import re
from bs4 import BeautifulSoup
from utils import MailUtils
from datetime import datetime, timedelta
import pytz
import logging
import threading
from django.http import Http404

from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver

from django.urls import resolve,reverse

def log_the_request(view_func):
    def log_decorator(request,*args, **kwargs):
        log("",logging.INFO,request)
        return view_func(request, *args, ** kwargs)
    return log_decorator


def log(msg,level,request):
    # {ip} {user} {asctime} {method} {path} {scheme} {session_id} {message}
    #pprint(dir(request.session))
    extra = dict()

    if 'REMOTE_ADDR' in request.headers:
        extra['ip'] = request.headers['REMOTE_ADDR']
    else:
        extra['ip'] = "-"

    if hasattr(request,'user'):
        if not request.user.is_anonymous:
            extra['user'] = request.user.id
        elif request.method == 'POST':
            for key in ('username','email'):
                if key in request.POST:
                    extra['user'] = request.POST[key]
                    break

        if not 'user' in extra:
            extra['user'] = '-'

    extra['path'] = request.get_full_path_info()
    extra['method'] = request.method
    extra['scheme'] = request.scheme

    extra['session_id'] = request.session.session_key
    # do not log session_id as is, log its hash: owasp guideline
    if extra['session_id'] is not None:
        h = blake2b(extra['session_id'].encode('utf-8'),digest_size=20)
        extra['session_id'] = h.hexdigest()

    logger = logging.getLogger("app")
    logger.log(level,msg,extra=extra)


@receiver(user_logged_in)
def post_login(sender, user, request, **kwargs):
    log("login successful", logging.INFO, request)
    if user.is_superuser:
        return

    user = UserSettings.objects.filter(user_id=user.id).exclude(appid="")
    if user:
        user = user[0]
        request.session['appid'] = user.appid


@receiver(user_logged_out)
def post_logout(sender,user, request, **kwargs):
    log("user logged out", logging.INFO, request)


@receiver(user_login_failed)
def on_login_failed(sender,request,**kwrgs):
    log("Error:login failed",logging.INFO, request)


@log_the_request
def index(request):
    return render(request, 'landing.html', {})


@log_the_request
def register_from_landing(request):
    email = None
    if request.method == 'POST':
        email = request.POST['email']

    return render(request,'web/register_user.html', {'email':email})


@log_the_request
def register_user(request):

    form = UserCreationForm()
    error = None

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password1']
        user_exists = User.objects.filter(username=username)

        if not user_exists:
            form = UserCreationForm(request.POST)
            if form.is_valid():
                form.save()
                user = authenticate(request, username=username, password=password)
                print(user)

                if user is not None:
                    with transaction.atomic():

                        appid = AppIdStore.objects.select_for_update(skip_locked=True).filter(assigned=False).first()
                        if appid:
                            print("email got", appid.app_id, " assigned:", appid.assigned)
                            us = UserSettings(user_id=user, appid=appid.app_id)
                            us.save()
                            user.email = user.username
                            user.save()
                            appid.assigned = True
                            appid.save()

                            request.session['appid'] = appid.app_id
                            login(request,user)

                            log("New user signed up:"+username, logging.INFO,request)

                            return redirect(reverse('tour'))
                        else:

                            log("[****ATTN***]Critical:user creation failed due to insufficient emails:"+username,logging.ERROR,request)
                            error = "Oops,something went wrong! This is unusual and we are very sorry. " \
                                    "We will fix the issue and get back to you on email you just provided." \
                                    "Thank you - Team Kleeppr"
                else:
                    error = "Automatic user authentication failed. Please try again. "
            else:
                error = "Ouch ..error occurred processing input. Please try again."
                for err in form.errors:
                    error += err+":"+form.errors[err]
        else:
            error = "Ooops..Email address is already taken. Try again or use password reset link to recover your account."

        log("Error: user registration failed:" + username + ", error:" + error, logging.ERROR, request)

    return render(request,'web/register_user.html', {'form':form, 'extra_context':{ 'error':error}})


@log_the_request
@login_required
def user_feed(request,nwl_id=None,filterConfirmation=False):

    feed = Feed.objects.filter(user_id = request.user.id).order_by('-ts')
    nwl = None
    error = ""

    if nwl_id:
        feed = feed.filter(nwl_id = nwl_id)
        nwl = Newsletters.objects.filter(id = nwl_id).first()
        if not nwl:
            error = "[1023] Sorry. Its strange but couldn't find newsletter in our records. This must be an error. "
    else:
        feed = feed.filter(is_confirmation=filterConfirmation)

    paginator = Paginator(feed, per_page=10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    #match = resolve('/list/58')
    #print(match.url_name)

    context = { 'nwl':nwl, 'page_obj':page_obj, 'error':error }
    return render(request, "feed.html",context=context)

@log_the_request
@login_required
def recent_feed(request):
    now = datetime.utcnow()
    two_wks_ago = now - timedelta(days=14)

    feed = Feed.objects.filter(user_id=request.user.id).filter(ts__range=(two_wks_ago,now)).distinct('nwl_id')
    m = []
    for f in feed:
        x = Feed.objects.filter(user_id=request.user.id).filter(nwl_id=f.nwl_id).filter(ts__range=(two_wks_ago,now)).order_by('-ts','nwl_id__frequency')[0]
        m.append(x)

    paginator = Paginator(m, per_page=10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'page_obj': page_obj }
    return render(request, "feed.html", context)

@log_the_request
@login_required
def get_letter(request, message_id):

    feed_rec = Feed.objects.filter(user_id=request.user.id).filter(message_id=message_id).first()
    if not feed_rec:
        log("feed record not found for user:%s, message_id:%s" % (request.user,message_id), logging.ERROR)
        raise Http404("Something weired has happened. We can't serve your request. Please try again")

    mailts = feed_rec.ts.astimezone(pytz.utc)
    mailts = mailts.strftime("%a, %d %b %H:%M:%S")
    mailts = "%s UTC" % mailts

    feed_rec.has_been_read = True
    feed_rec.save()

    context = { 'ts':mailts, 'message_id':message_id, 'title':feed_rec.subject, 'letter':feed_rec.nwl_id.letter, 'author':feed_rec.nwl_id.author }
    return render(request, 'letter.html',context)


@log_the_request
@login_required
@xframe_options_exempt
def get_letter_content(request,message_id):

    app_id_record = AppIdStore.objects.filter(app_id=request.session['appid']).first()
    if not app_id_record:
        log("app_id record not found for %s" % request.session['appid'], logging.ERROR)
        raise Http404("Something weired has happened. We can't serve your request. Please try again")

    imap_user = app_id_record.app_id
    imap_secret = app_id_record.app_id_secret

    mbox = Imapbox(settings.IMAP_HOST, imap_user, imap_secret)
    email = mbox.get_message_by_id(message_id)
    #print(email.get_body())

    #
    soup = BeautifulSoup(email.get_body().get_content(), 'html.parser')
    for href in soup.find_all('a'):
        href['target'] = '_blank'

    return HttpResponse(str(soup))


@log_the_request
@login_required
def my_sub(request):

    subscriptions = UserSubs.objects.filter(user_id=request.user)
    paginator = Paginator(subscriptions, per_page=25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "mysub.html", { 'page_obj':page_obj })


@log_the_request
def explore(request,tag="all"):
    tag = tag.strip()
    if tag != "all":
        print("tag:",tag)
        letters = Newsletters.objects.filter(tags__tag=tag).order_by('id')
    else:
        letters = Newsletters.objects.order_by('id')

    letters = [ letter for letter in letters if letter.is_complete() ]

    paginator = Paginator(letters, per_page=25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    tags = Tags.objects.filter().values_list('tag',flat=True)
    follow = None
    if 'follow' in request.session:
        follow = request.session['follow']
        del request.session['follow']

    return render(request, "explore.html", { 'page_obj':page_obj, 'tags':tags, 'follow':follow })


@log_the_request
@login_required
def bookmark(request):
    user = UserSettings.objects.filter(user_id=request.user.id)
    if user:
        user = user[0]
    return render(request,'bookmarklet.html',{'appid':user.appid})


@log_the_request
def follow(request, next):
    nwl = Newsletters.objects.filter(pk=next).values('letter','url','author')
    if nwl:
        nwl = nwl[0]

    request.session['follow'] = nwl

    if not request.user.is_authenticated:
        return redirect(reverse('register'))
    else:
        return redirect('/explore')


@log_the_request
def search_letters(request):
    print("assdsad")
    if request.method == 'POST':
        term = request.POST['term']
        print("term",term)
        letters = Newsletters.objects.filter(
            Q(letter__icontains=term) |
            Q(desc__icontains=term) |
            Q(author__icontains=term) |
            Q(url__icontains=term) |
            Q(tags__tag__icontains=term)
        )

        paginator = Paginator(letters, per_page=25)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, "explore.html", {'page_obj': page_obj, 'term': term})
    else:
        return redirect('/explore')


@log_the_request
@login_required
def tour(request,welcome=False):
    return render(request,"tour.html",{'welcome':False })


def terms(request,show='tc'):
    if show == 'pp':
        return render(request,"privacy-policy.html")
    elif show == 'tc':
        return render(request, "terms-and-conditions.html")
    elif show == 'ck':
        return render(request, "cookie-policy.html")