"""sheet_music_africa URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static


from rest_framework_simplejwt import views as jwt_views

from composer.serializer import CustomJWTSerializer

from password.views import updatePassword, checkToken, generatePasswordToken

from musicStore.views import redirect_to_frontend,redirect_song_to_frontend,redirect_composer_to_frontend

urlpatterns = [
    path('admin/', admin.site.urls),
    path('store/', include('musicStore.urls')),
    path('user/', include('composer.urls')),
    path('help/', include('help_center.urls')),
    path('payout/', include('payout.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('api/token/', jwt_views.TokenObtainPairView.as_view(
        serializer_class=CustomJWTSerializer), name='token_obtain_pair'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(),
         name='token_refresh'),

    # reset password url
    path('forgot-password/', generatePasswordToken, name='forgot-password'),
    path('check-token/', checkToken, name='check-token'),
    path('update-password/', updatePassword, name='update-password'),

    #redirect to frontend
    path('<str:path>/<str:param>', redirect_song_to_frontend,name='redirect_to_frontend'),
    path('', redirect_to_frontend,name='redirect_to_frontend'),
    path('<str:path>', redirect_composer_to_frontend,name='redirect_to_frontend'),

]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

