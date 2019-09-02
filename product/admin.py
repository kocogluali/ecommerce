from django.contrib import admin
from .models import *
# from accounts.models import UrunSiparisler, UrunSiparisAttr
# import django_filters
from django.contrib.auth.models import User
from django.contrib import messages


class FilesInline(admin.TabularInline):
    model = Files
    extra = 0


class ProductAdmin(admin.ModelAdmin):
    # prepopulated_fields = {'slug': ('title',), }
    # list_display = ('id', 'title')

    class Meta:
        model = Product
        fields = ['title', 'brand', 'price']

    readonly_fields = ('date', 'slug')
    # inlines = [FilesInline]


# class Admin_Urunler(admin.ModelAdmin):
#     class Meta:
#         model = Product
#
#     inlines = [FilesInline]


class BrandsAdmin(admin.ModelAdmin):
    class Meta:
        model = Brands


class DetailInline(admin.TabularInline):
    model = Detail
    extra = 0


class VariantInline(admin.StackedInline):
    model = Variant
    extra = 0


class SubAttrInline(admin.TabularInline):
    model = Sub_Attr
    extra = 0


class AdminUrunler(admin.ModelAdmin):
    list_display = ('id', 'title', 'price', 'sub_menu', 'voteAverage')
    list_display_links = ('id', 'title',)

    class Meta:
        model = Product

    fieldsets = [
        ('Genel Bilgiler', {'fields': ['title', 'main_menu', 'sub_menu', 'image', 'info', 'stock', 'price']}),
        ('Diğer Bilgiler', {'fields': ['active', 'brand', 'slug', 'tags', 'voteAverage']}),
        ('İndirim', {'fields': ['disc_price', 'disc_group']}),

    ]
    readonly_fields = ('date', 'slug')
    inlines = [DetailInline, VariantInline, FilesInline]
    list_filter = ('main_menu', 'sub_menu', 'active')
    search_fields = ("title", "info", "code")

    def save_model(self, request, obj, form, change):
        if obj.disc_price and obj.disc_group:
            messages.add_message(request, messages.ERROR, "Hata : Ürüne aynı anda  indirim grubu ve indirimli fiyat girilemez.Lütfen sadece birini seçiniz")
            # raise ValueError("iki aynanda olmaz")
        else:
            obj.save()
        # super(AdminUrunler, self).save_model(request, obj, form, change)


class DetailAdmin(admin.ModelAdmin):
    list_display = ('id', 'parent_attr', 'product')
    list_display_links = ('id', 'parent_attr', 'product')

    class Meta:
        model = Detail


class VariantAdmin(admin.ModelAdmin):
    list_display = ('id', 'product')

    class Meta:
        model = Variant


class AttributeAdmin(admin.ModelAdmin):
    list_display = ("id", "name")

    class Meta:
        model = Attribute

    inlines = [SubAttrInline]


class SubAttributeAdmin(admin.ModelAdmin):
    list_display = ("id", "parent", "title")

    class Meta:
        model = Sub_Attr


class SubDetailAdmin(admin.ModelAdmin):
    class Meta:
        model = SubDetail

    list_display = ('title', 'sub_detail')


admin.site.register(SubDetail, SubDetailAdmin)
admin.site.register(Sub_Attr, SubAttributeAdmin)

admin.site.register(Detail, DetailAdmin)
admin.site.register(Attribute, AttributeAdmin)
admin.site.register(Variant, VariantAdmin)
admin.site.register(Brands, BrandsAdmin)
admin.site.register(Product, AdminUrunler)
