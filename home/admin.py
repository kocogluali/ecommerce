from django.contrib import admin
from .models import *


class tabularInlıne(admin.TabularInline):
    class Meta:
        model = AnaMenu


admin.site.register(AnaMenu)
admin.site.register(AltMenu)
admin.site.register(Banner)
