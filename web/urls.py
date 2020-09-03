from django.urls import path,include
from django.contrib.auth.views import LoginView
from .views import log_the_request
from . import views
from django.contrib.auth import views as auth_views

# indus is account management prefix
urlpatterns = [
    path('', views.index, name='index'),
    path('indus/', include('django.contrib.auth.urls')),
    path('indus/password_reset/', log_the_request(auth_views.PasswordResetView.as_view()), name='password_reset'),
    path('indus/reset/<uidb64>/<token>/', log_the_request(auth_views.PasswordResetConfirmView.as_view()), name='password_reset_confirm'),
    path('indus/register',views.register_user,name='register'),
    path('indus/register/<follow>',log_the_request(views.register_user),name='register_follow'),

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
    path('tour',views.tour,name='tour')
]
