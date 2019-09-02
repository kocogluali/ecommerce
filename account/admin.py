from django.contrib import admin
from .models import *


class AdressAdmin(admin.ModelAdmin):
    list_display = ('id', 'adres_name','name', 'last_name')

    class Meta:
        model = Adress


class CityAdmin(admin.ModelAdmin):
    # list_display = ('id','title')
    class Meta:
        model = City


class TownAdmin(admin.ModelAdmin):
    # list_display = ('id','title')
    class Meta:
        model = Province


class CargoAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'delivery_time')

    class Meta:
        model = Cargo


class SepetInline(admin.TabularInline):
    model = SepetUrunler
    extra = 2
    readonly_fields = ("price", "totalPrice", "attr", "details", "qty")


class SepetAdmin(admin.ModelAdmin):
    inlines = [SepetInline]
    list_display = ('id', 'user', 'user_ip')
    list_display_links = ('id', 'user', 'user_ip')

    class Meta:
        model = Sepet


class SepetUrunAdmin(admin.ModelAdmin):
    list_display = ('id', 'parent_product')
    list_display_links = ('id', 'parent_product')
    readonly_fields = ("price", "totalPrice", "attr", "details", "qty")

    class Meta:
        model = SepetUrunler


class TamSiparislerAdmin(admin.ModelAdmin):
    class Meta:
        model = TamSiparisler

    readonly_fields = ["adres_text", "product_text", 'date', 'mail']


class couponAdmin(admin.ModelAdmin):
    class Meta:
        model = Coupon

    list_display = ("title", "code", "active", "qty", "last_date")


admin.site.register(TamSiparisler, TamSiparislerAdmin)
admin.site.register(Favorites)
admin.site.register(Sepet, SepetAdmin)
admin.site.register(SepetUrunler, SepetUrunAdmin)
admin.site.register(Cargo, CargoAdmin)
admin.site.register(Adress, AdressAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(Province, TownAdmin)
admin.site.register(Coupon, couponAdmin)
