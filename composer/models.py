from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from musicStore.models import Score_sale

import decimal
default_decimal = decimal.Decimal(0.0)


class ComposerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    pic = models.FileField(null=True, blank=True)
    can_sell = models.BooleanField(default=False)
    country = models.CharField(max_length=100, default="Nigeria", blank=True)
    country_short_code = models.CharField(
        max_length=2, default="NG", blank=True)
    # current_sales_percentage = models.PositiveIntegerField(default=80)
    current_sales = models.DecimalField(
        max_digits=10, decimal_places=2, default=default_decimal)
    all_time_sales = models.DecimalField(
        max_digits=10, decimal_places=2, default=default_decimal)

    # new fields
    discription = models.TextField(default="", blank=True)
    background_image = models.FileField(null=True, blank=True)

    # social link
    facebook_link = models.TextField(default="", blank=True)
    twitter_link = models.TextField(default="", blank=True)
    youtube_link = models.TextField(default="", blank=True)
    soundcloud_link = models.TextField(default="", blank=True)
    can_verify = models.BooleanField(default=False)

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name


class ComposerAccount(models.Model):
    composer = models.OneToOneField(ComposerProfile, on_delete=models.CASCADE)
    bank_name = models.CharField(max_length=50, blank=True)
    bank_code = models.CharField(max_length=10, blank=True)
    account_number = models.CharField(max_length=50, blank=True)
    email = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return "%s account detail" % self.composer.user.first_name


class FollowComposer(models.Model):
    main_composer = models.ForeignKey(
        ComposerProfile, on_delete=models.CASCADE, related_name="main_composer")
    other_composer = models.ForeignKey(
        ComposerProfile, on_delete=models.CASCADE, related_name="other_composer")

    def __str__(self):
        return self.other_composer.user.first_name + " follows " + self.main_composer.user.first_name


# hisory of items in cart that we want to pay for
class UserPaymentHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0)
    currency = models.CharField(max_length=10, default="USD")
    cart_item = models.ManyToManyField(Score_sale)
    verified = models.BooleanField(default=False)  # under consideration
    date = models.DateTimeField(default=timezone.now)
    payment_type = models.CharField(max_length=100, default="payin")

    def __str__(self):
        return self.user.first_name


class UserPaymentLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    log_type = models.CharField(max_length=10, default="sales")
    currency = models.CharField(max_length=10, default="USD")

    bank_paid_to = models.CharField(max_length=30,blank=True,null=True)
    email_paid_to = models.CharField(max_length=20,blank=True,null=True)
    bank_name_paid_to = models.CharField(max_length=50,blank=True,null=True)

    def __str__(self):
        return self.user.first_name



class Subscriber(models.Model):
    name = models.CharField(max_length=200,blank=True)
    email = models.EmailField()
    date_subscribed =  models.DateField(default = timezone.now)

    def __str__(self):
        return self.email