from django.contrib.auth.models import User
from django.http import HttpResponse

from account.models import SepetUrunler, Favorites, Sepet
from product.models import Product


def removeBasketItem(request):
    basketItemID = request.GET.get("basket_item_id")
    try:
        SepetUrunler.removeBasketItem(SepetUrunler, basketItemID)
        data = "Ürün Başarıyla Silindi"
    except Exception as e:
        data = "Ürün Silinirken hata Oluştu" + str(e) + ""
    return HttpResponse(data)


def addFavoritesItem(request):
    productID = request.GET.get("productID")
    try:
        user = User.objects.get(id=request.user.id)
    except:
        user = None
    try:
        product = Product.objects.get(id=productID)
    except:
        product = None
    if user and product:
        favorite = Favorites.objects.get(user=user)
        favorite.fav_p.add(product)
        message = "İstek Listeme başarıyla eklendi"
    else:
        message = "Kullanıcı Girişi Yapılmadı"
    return HttpResponse(message)


def removeFavItems(request):
    userID = request.GET.get("userID")
    productID = request.GET.get("productID")
    try:
        product = Product.objects.get(id=productID)
        items = Favorites.objects.get(user__id=userID).fav_p
        items.remove(product)
        data = "Ürün Başarıyla Silindi"
    except Exception as e:
        data = "Ürün Silinirken hata Oluştu" + str(e) + ""
    return HttpResponse(data)


def apply_coupon(request):
    from account.models import Coupon
    import json
    code = request.GET.get("code")
    basketID = request.GET.get("basketID")
    try:
        coup = Coupon.getCoupon(Coupon, code)
        basket = Sepet.objects.get(id=basketID)
    except:
        coup = None
        basket = None
    try:
        if coup and basket:
            basket.coupon = coup
            basket.save(update_fields=["coupon"])
            discPrice = coup.disc_price
            message = "Kupon Uygulandı"
            status = True
        else:
            discPrice = 0
            message = "Geçersiz Kupon Kodu"
            status = False

    except:
        status = False

    data = json.dumps({
        'messages': message,
        'discPrice': str(discPrice),
        'status': status,
    })
    return HttpResponse(data)
