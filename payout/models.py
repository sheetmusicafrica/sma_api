from django.db import models
from django.utils import timezone

from composer.models import UserPaymentLog, ComposerProfile


class BatchPayout(models.Model):
    provider = models.CharField(max_length=20)
    date = models.DateField()
    month = models.PositiveIntegerField(blank=True, null=True)
    year = models.PositiveIntegerField(blank=True, null=True)
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)
    batch_number = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, default="pending")
    completed = models.BooleanField(default=False)
    full = models.BooleanField(default=False)
    composers_paid_to = models.ManyToManyField(
        ComposerProfile, blank=True)

    def __str__(self):
        return "%s payment for %d-%d" % (self.provider, self.month, self.year)

    def set_month_and_year(self):
        date = self.date
        self.month = date.month
        self.year = date.year
        self.save()
