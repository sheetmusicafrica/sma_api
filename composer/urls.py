from django.urls import path, include

from rest_framework.routers import DefaultRouter
from rest_framework import renderers

from . import views


router = DefaultRouter()
router.register(r'composer', views.ComposerView, basename="composer")
router.register(r'relationship', views.ComposerRelationshipView,
                basename="relationship")

urlpatterns = [
    path('subscribe/', views.subscribe, name='subscribe'),
    path('register/', views.RegisterUser.as_view(), name='RegisterUser'),
    path('get-user/', views.getUser.as_view(), name='getUser'),
    path('change-password/', views.ChangePassword.as_view(), name='ChangePassword'),
    path('get-payment-info/', views.getPaymentinfo.as_view(), name='getPaymentinfo'),
    path('get-payment-log/', views.getPaymentHistory.as_view(),
         name='getPaymentHistory'),

    path('get-purchased-score/<int:song>',
         views.getPurchasedScore, name='getPurchasedScore'),

    path('subscribe/',
         views.mangeComposerRelationship, name='mangeComposerRelationship'),
    path('get-pdf', views.GeneratePdf.as_view()),
    path('account-info/', views.GetComposerAccountInfo.as_view()),
    path('withdrawl/', views.WithdrawlRevenue.as_view()),
    path('paypal/', views.testpaypal),
    path('', include(router.urls)),

]
