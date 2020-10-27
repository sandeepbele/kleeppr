from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from utils import MailUtils


class Tags(models.Model):
    tag = models.TextField(unique=True,default="")

    def __str__(self):
        return str(self.tag)


class Publisher(models.Model):
    name = models.TextField()
    domain = models.TextField()
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return str(self.name)


class Newsletters(models.Model):
    list_id = models.TextField(null=True)
    letter = models.TextField(null=True)
    sender_email = models.TextField(null=True)
    url = models.TextField(null=True)
    desc = models.TextField(null=True)
    author = models.TextField(null=True)
    author_url = models.TextField(null=True)
    frequency = models.TextField(choices=[("D","daily"),("W","weekly"),("FW","few times a week"),
                                          ("M","monthly"),("FW","few times a month"),("R","random")],null=True)
    tags = models.ManyToManyField(Tags)
    extra_info = models.TextField(null=True,default="None")

    is_active = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at = models.DateTimeField(auto_now=True,null=True)

    publisher = models.ForeignKey(Publisher,default=None,on_delete=models.CASCADE)

    def get_tags(self):
        tags = self.tags.all().values_list('tag',flat=True)
        if tags:
            return ",".join(tags)
        else:
            return "uncategorized"

    def get_frequency(self):
        a = {"D":"daily","W":"weekly"}
        key = str(self.frequency)
        if key in a:
            return a[key]
        else:
            return "NA"

    def is_complete(self):
        for f in [self.letter, self.tags, self.frequency, self.url, self.sender_email, self.author, self.desc ]:
            if f is None or f == "" or f == "unknown" or f == "NA":
                return False

        return True

    def __str__(self):
        return self.letter or ""


class Feed(models.Model):

    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    message_id = models.TextField(null=True)
    ts = models.DateTimeField(default=datetime.utcnow,null=True)
    nwl_id = models.ForeignKey(Newsletters, on_delete=models.CASCADE)
    is_confirmation = models.BooleanField(default=False)
    subject = models.TextField(null=True)
    intro = models.TextField(null=True)
    has_been_read= models.BooleanField(default=False)

    def get_x_time_ago(self):
        return MailUtils.get_x_time_ago(self.ts.strftime("%a, %d %b %Y %X %z"))


class UserSettings(models.Model):

    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField(null=True)
    appid = models.TextField(null=True)
    feeder_ts = models.DateTimeField(null=True)
    email_verified = models.BooleanField(null=True, default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)


class UserSubs(models.Model):

    user_id = models.ForeignKey(User,on_delete=models.CASCADE)
    nwl_id = models.ForeignKey(Newsletters, on_delete=models.CASCADE)
    unsub_url = models.TextField(null=True)
    feed_count = models.IntegerField(default=0)
    sub_ts= models.DateTimeField(auto_now_add=True, null=True)

    def has_confirmation_email(self):
         f = Feed.objects.filter(user_id=self.user_id).filter(nwl_id=self.nwl_id).\
            filter(is_confirmation=True)
         return f.exists() and self.feed_count > 0


class AppIdStore(models.Model):

    app_id = models.TextField()
    app_id_secret = models.TextField()
    assigned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    assigned_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return str(self.id)
