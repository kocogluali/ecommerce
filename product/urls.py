from django.contrib import admin
from django.urls import path
from .views import *

app_name = "shop"

urlpatterns = [
    # AJAX REQUEST
    path('urun_fiyat_getir', urun_fiyat_getir, name="urun_fiyat_getir"),
    path('product_filter', product_filter, name="product_filter"),
    # END AJAX REQUEST
    path('<slug:slug>/', product_list, name="product_list"),  # Main Cat burada categoriler listelencek
    path('<slug:category>/<slug:product>/', product_detail, name="product_detail"),


]
