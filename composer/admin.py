from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(ComposerProfile)
admin.site.register(UserPaymentHistory)
admin.site.register(UserPaymentLog)
admin.site.register(ComposerAccount)
admin.site.register(FollowComposer)
admin.site.register(Subscriber)
