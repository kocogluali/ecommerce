from django.contrib import admin
from .models import SSS


class SSSAdmin(admin.ModelAdmin):
    class Meta:
        model = SSS
    list_display = ("title","date")


admin.site.register(SSS,SSSAdmin)