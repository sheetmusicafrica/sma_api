from django.urls import path, include

from rest_framework.routers import DefaultRouter
from rest_framework import renderers

from . import views



urlpatterns = [
    path('payout/<int:amount>', views.payoutTest, name='payoutTest'),
]
