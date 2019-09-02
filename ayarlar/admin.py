from django.contrib import admin
from .models import *


class SiteAdmin(admin.ModelAdmin):
    class Meta:
        model = SiteSettings
    list_display = ('id','title','domain','desc')
    list_display_links = ('id','title','domain','desc')

    def has_add_permission(self, request):
        count = SiteSettings.objects.all().count()
        if count < 1:
            return True
        else:
            return False

    def save_model(self, request, obj, form, change):
        obj.save()
        if not request.user.username == "adminm":
          raise Exception("Bu Bilgileri Güncelleme Yetkiniz Yok (required admin login)")


    fieldsets = [
        ('Genel Bilgiler', {
            'fields': ['title', 'desc', 'logo', 'logo_nav', 'icon', 'keywords', 'footer_text', 'top_banner',
                       'post_detail','domain','page_size','gmap']}),
        ('Sosyal Medya', {'fields': ['instagram', 'facebook', 'twitter', 'pinterest', 'google_plus', 'tumblr']}),
        ('İletişim Bilgileri',{'fields':['phone','adres','mail']}),
        ('İyzico Ödeme Ayarları',{'fields':['iyzi_api','iyzi_secret_key']}),
        ('Google Analytics',{'fields':['jsonFile','view_id']},)
    ]


class ModulAdmin(admin.ModelAdmin):
    class Meta:
        model = Moduller
    list_display = ('id','title','banner','durum')
    list_display_links = ('id','title','banner','durum')

    def save_model(self, request, obj, form, change):
         if not request.user.username == "adminm":
            raise Exception("Bu Bilgileri Güncelleme Yetkiniz Yok (required admin login)")
         else:
             obj.save()


# admin.site.register(Profile)
admin.site.register(Moduller,ModulAdmin)
admin.site.register(Languages)
admin.site.register(SiteSettings, SiteAdmin)
