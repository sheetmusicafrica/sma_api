from django.urls import path, include

from rest_framework.routers import DefaultRouter
from rest_framework import renderers

from . import views


router = DefaultRouter()
router.register(r'genre', views.GenreView, basename="genre")
router.register(r'sheet', views.SheetMusicView, basename="store")
router.register(r'cart', views.CartView, basename="cart")
router.register(r'review', views.SheetReviewView, basename="review")

urlpatterns = [
    path('', include(router.urls)),
    path('sales', views.getSales.as_view(), name='getSales'),
    path('add_to_cart', views.AddToCart.as_view(), name='AddToCart'),
    path('digital-libary', views.GoToDigitalLibary.as_view(),name='GoToDigitalLibary'),
    path('get-payment-link/', views.get_checkout_link, name='get_checkout_link'),
    path('verify-payment/', views.verifyPayment, name='verifyPayment'),
    path('song-info/<int:id>', views.getMoreInfoOnSheetMusic,name='getMoreInfoOnSheetMusic'),
    path('download/<int:id>', views.downloadScore,name='downloadScore'),

    path('unverified-song/', views.getUnverifiedSongs,name='getUnverifiedSongs'),
    path('mark-song/', views.markSong,name='markSong'),
    path('share/<str:link>', views.deapLink,name='deapLink'),
]
