from django.contrib import admin
from .models import Competition,GameProfile,ScoreLog


admin.site.register(Competition)
admin.site.register(GameProfile)
admin.site.register(ScoreLog)