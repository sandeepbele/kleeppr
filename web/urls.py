from django.conf.urls import url
from django.urls import path,include,re_path
from django.contrib.auth.views import LoginView
from .views import log_the_request
from . import views
from django.contrib.auth import views as auth_views
#from django.views.generic.base import RedirectView

#favicon_view = RedirectView.as_view(url='/static/favicon.ico', permanent=True)

# indus is account management prefix
urlpatterns = [
    path('', views.search, name='index'),
    path('indus/', include('django.contrib.auth.urls')),
    path('indus/password_reset/', log_the_request(auth_views.PasswordResetView.as_view()), name='password_reset'),
    path('indus/reset/<uidb64>/<token>/', log_the_request(auth_views.PasswordResetConfirmView.as_view()), name='password_reset_confirm'),
    path('register_from_landing',views.register_from_landing,name='register_from_landing'),
    path('indus/register',views.register_user,name='register'),
    path('indus/register/<follow>',log_the_request(views.register_user),name='register_follow'),
    #path('indus/login',auth_views.LoginView.as_view(),{'msg':None},name="login_with_msg"),
    path('feed', views.user_feed, name='feed'),
    path('feed/<int:nwl_id>',views.user_feed,name='nwl_feed'),
    path('confirmsub',views.user_feed,{'filterConfirmation':True},name='confirmsub',),
    path('letter/<int:message_id>',views.get_letter, name='letter'),
    path('letter_content/<int:message_id>',views.get_letter_content, name='letter_content'),
    path('mysub',views.my_sub,name='mysub'),
    path('explore',views.explore,name='explore'),
    path('explore/<tag>',views.explore,name='tag_explore'),
    path('bookmark',views.bookmark,name='bookmark'),
    path('follow/<int:next>',views.follow,name='follow'),
    path('search',views.search_letters,name="search_explore"),
    path('tour',views.tour,name='tour'),
    path('welcome',views.tour,{'welcome':True},name='welcome'),
    path('recent', views.recent_feed,name='recent'),
    path('privacy', views.terms,{ 'show':'pp'} ,name='privacy'),
    path('cookie', views.terms,{ 'show':'ck'} ,name='cookie'),
    path('terms', views.terms,{ 'show':'tc'} ,name='terms'),
    path('error',views.error,name='error'),
    path('about', views.index,name="about"),
    path('e', views.search,name='search'),
    url(r'^activate_account/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
                views.ActivateAccountView.as_view(), name='activate_account'),

    #re_path(r'^favicon\.ico$', favicon_view),
]
