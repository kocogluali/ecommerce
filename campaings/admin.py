from django.contrib import admin
from .models import Campaign


class CampaignAdmin(admin.ModelAdmin):
    readonly_fields = ("slug",)

    def has_add_permission(self, request):
        count = Campaign.objects.filter(active=True).count()
        if count < 1:
            return True
        else:
            return False

    class Meta:
        model = Campaign


admin.site.register(Campaign, CampaignAdmin)