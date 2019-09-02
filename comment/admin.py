from django.contrib import admin
from .models import *


class ProductCommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'active', 'content','votes']
    list_display_links = ['user', 'product']

    def save_model(self, request, obj, form, change):
        if obj.id and obj.active:
            obj.save()
            ProductsComments.updateProductAverage(ProductsComments, obj.product)

    class Meta:
        model = ProductsComments


admin.site.register(ProductsComments, ProductCommentAdmin)


class BlogCommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'blog', 'active']
    list_display_links = ['user', 'blog']

    class Meta:
        model = BlogComments


admin.site.register(BlogComments, BlogCommentAdmin)
