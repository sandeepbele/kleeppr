from django.contrib import admin
from .models import Newsletters,UserSettings,UserSubs,Feed,Tags,Publisher,AppIdStore
# Register your models here.

admin.site.register(Tags)


class IsCompleteFilter(admin.SimpleListFilter):
    title = 'is complete?'
    parameter_name = 'is_complete'

    def lookups(self, request, model_admin):
       """
           List of values to allow admin to select
       """
       return (
          ('True', 'True'),
          ('False', 'False')
       )

    def queryset(self, request, queryset):
        """
         Return the filtered queryset
        """
        if self.value() == 'True':
            print("here")
            l = [x.id for x in queryset if x.is_complete()]
            return queryset.filter(pk__in=l)
        elif self.value() == 'False':
            l = [x.id for x in queryset if not x.is_complete()]
            return queryset.filter(pk__in=l)
        else:
            return queryset


class NewslettersAdmin(admin.ModelAdmin):
    list_display = ('list_id','letter', 'author', 'sender_email', 'desc', 'is_complete')
    search_fields = ('letter','author','tags__tag','sender_email','desc')
    list_filter = ['frequency',IsCompleteFilter]


class PublishersAdmin(admin.ModelAdmin):
    list_display = ('name','domain','is_verified')
    search_fields = ('name','domain')

class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ('user_id','appid','created_at')
    search_fields = ('user_id','appid')


class HasEmailConfirmationFilter(admin.SimpleListFilter):
    title = 'has_comfirmation_email'
    parameter_name = 'has_comfirmation_email'

    def lookups(self, request, model_admin):
       """
           List of values to allow admin to select
       """
       return (
          ('True', 'True'),
          ('False', 'False')
       )

    def queryset(self, request, queryset):
        """
         Return the filtered queryset
        """
        if self.value() == 'True':
            print("here")
            l = [x.id for x in queryset if x.has_confirmation_email()]
            return queryset.filter(pk__in=l)
        elif self.value() == 'False':
            l = [x.id for x in queryset if not x.has_confirmation_email()]
            return queryset.filter(pk__in=l)
        else:
            return queryset


class UserSubsAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'nwl_id','feed_count','has_confirmation_email')
    search_fields = ('user_id', 'nwl_id')
    list_filter = [HasEmailConfirmationFilter]


class FeedAdmin(admin.ModelAdmin):
    list_display = ('user_id','nwl_id','ts','is_confirmation')


class AppIdStoreAdmin(admin.ModelAdmin):
    list_display = ['app_id','assigned']
    list_filter = ['assigned']


admin.site.register(Newsletters, NewslettersAdmin)
admin.site.register(UserSettings, UserSettingsAdmin)
admin.site.register(UserSubs,UserSubsAdmin)
admin.site.register(Feed,FeedAdmin)
admin.site.register(Publisher,PublishersAdmin)
admin.site.register(AppIdStore, AppIdStoreAdmin)
