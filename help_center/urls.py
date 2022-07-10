from rest_framework.routers import DefaultRouter
from rest_framework import renderers

from django.urls import path, include

from . import views


router = DefaultRouter()
router.register(r'help-center', views.ManagePost, basename="help-center")


urlpatterns = [
    path('', include(router.urls)),
    path('give-feedback/', views.Postfeedback.as_view(), name='Postfeedback'),
]
