from django.urls import path
from .views import *
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import views as auth_views
from django.conf.urls import url
from account import AjaxView

app_name = "accounts"

urlpatterns = [
    # AJAX URLS
    path('update_cart', update_cart, name="update_cart_AJAX"),
    path('remove_basket_item', AjaxView.removeBasketItem, name="remove_basket_item"),
    path('remove_fav_items', AjaxView.removeFavItems, name="removeFavItems"),
    path('add_favorite_item', AjaxView.addFavoritesItem, name="addFavoritesItem"),
    path('apply_coupon/', AjaxView.apply_coupon, name="apply_coupon"),
    # END AJAX URLS
    path('sepetim', sepetim, name="myBasket"),
    path('favorilerim', favorilerim, name="myWishList"),
    path('odeme', checkout, name="checkout"),
    path('giris', loginView, name="login"),
    # iyzico and payment
    path('taksit_getir', taksit_getir, name="TaksitGetir"),
    path('checkout_done', csrf_exempt(checkout_done), name="checkout_done"),
    path('three-d-security', csrf_exempt(secure_view), name="secure_view"),
    path('cikis-yap', logout_view, name="logout"),

    path('password/', password, name='password'),  # <-- for social media auth
]
