from django.shortcuts import render

from account.subView import adresFormPostForCheckOutView, userLogin, userRegister, userBasketUpdateAfterUserLogin
from .models import *
from account.templatetags.accoTags import get_client_ip
from django.core import serializers
from django.http import HttpResponse, HttpResponseRedirect
from .forms import Adress_Form
import ssl, iyzipay, collections, json, base64
from .forms import LoginForm, RegisterForm
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from social_django.models import UserSocialAuth  # <-- for social media auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AdminPasswordChangeForm, PasswordChangeForm  # <-- for social media auth
from django.contrib.auth import update_session_auth_hash  # <-- for social media auth
from social_django.models import UserSocialAuth  # <-- for social media auth
from django.contrib import messages


# account iyzico And Installment
def taksit_getir(request):
    cart_number = str(request.GET.get('cart_number'))
    options = {
        'api_key': 'sandbox-pN5AwOUOtVHZW6ElUmlwTilUVQDG6ZyX',
        'secret_key': 'sandbox-s80sblJrFDBQqGAKIe2swHkZxAv3BJMH',
        'base_url': iyzipay.base_url
    }
    ssl._create_default_https_context = ssl._create_unverified_context
    # detail_id = request.GET.get('detail_id')
    basket_item_id = request.session["user_basket_id"]
    basket = Sepet.objects.get(id=basket_item_id)
    toplam = basket.sepet_tutar
    req = dict([('locale', 'tr')])
    req['conversationId'] = get_random_string(length=9, allowed_chars='0123456789')
    req['binNumber'] = cart_number[:6]
    req['price'] = str(toplam)
    installment_info = iyzipay.InstallmentInfo()
    installment_info_response = installment_info.retrieve(req, options)
    return HttpResponse(installment_info_response)
    # data = json.dumps({
    #     'taksit': str(installment_info_response),
    #     'price': str()
    # })
    # return HttpResponse(data)


def payment(request, basket, basketItems, taksit, selectedAdres, card, ip):
    status = None
    options = {
        'api_key': 'sandbox-pN5AwOUOtVHZW6ElUmlwTilUVQDG6ZyX',
        'secret_key': 'sandbox-s80sblJrFDBQqGAKIe2swHkZxAv3BJMH',
        'base_url': iyzipay.base_url
    }
    ssl._create_default_https_context = ssl._create_unverified_context
    try:
        adres_user = Adress.objects.get(id=selectedAdres)
        request.session["adres_id"] = adres_user.id
    except:
        adres_user = None
    payment_card = {
        'cardHolderName': str(card.holderName),
        'cardNumber': str(card.number),
        'expireMonth': str(card.expireMonth),
        'expireYear': str(card.expireYear),
        'cvc': str(card.CVC),
        'registerCard': '0'  # silinecek
    }
    if adres_user:
        if adres_user.user:
            id = str(adres_user.user.id)
            last_login = str(adres_user.user.last_login)
            register_date = str(adres_user.user.date_joined)
        else:
            id = str(get_random_string(10, allowed_chars='1234567890'))
            last_login = str(timezone.now())
            register_date = str(timezone.now())
        buyer = {
            'id': id,
            'name': str(adres_user.name),
            'surname': str(adres_user.last_name),
            'gsmNumber': str(adres_user.phone_number),
            'email': str(adres_user.mail),
            'identityNumber': '74300864791',  # kullanıcı tcsi tutulmuyor
            'lastLoginDate': last_login,
            'registrationDate': register_date,
            'registrationAddress': str(adres_user.adres),
            'ip': str(ip),
            'city': str(adres_user.city.title),
            'country': 'Turkey',
        }
        address = {
            'contactName': str(adres_user.name),
            'city': str(adres_user.city.title),
            'country': 'Turkey',
            'address': str(adres_user.adres),
            'zipCode': str(adres_user.postcode),
        }
        basket_items = []
        if basketItems:
            for item in basketItems:
                basket_items += \
                    {
                        'id': item.parent_product.id,
                        'name': str(item.parent_product.title.encode('utf-8')),
                        'category1': str(item.parent_product.main_menu),
                        'category2': str(item.parent_product.sub_menu),
                        'itemType': 'PHYSICAL',
                        'price': str(item.totalPrice),
                    },
        conversation_id = get_random_string(12, allowed_chars="123456789")
        request.session['conv_id'] = conversation_id
        req = {
            'locale': 'tr',
            'conversationId': str(conversation_id),
            'price': str(basket.sepet_tutar),
            'paidPrice': str(basket.sepet_tutar),
            'currency': 'TRY',
            'installment': str(taksit),
            'basketId': str(basket.id),
            'paymentChannel': 'WEB',
            'paymentGroup': 'PRODUCT',
            'paymentCard': payment_card,
            'buyer': buyer,  # buyer gelmeyebilir ?
            'shippingAddress': address,
            'billingAddress': address,
            'basketItems': basket_items,
            "callbackUrl": "http://127.0.0.1:8000/kullanici/checkout_done",
        }
        payment = iyzipay.ThreedsInitialize().create(req, options)
        response = payment.read().decode('utf-8')
        json_response = json.loads(response)
        if json_response['status'] == 'success':
            secure = base64.urlsafe_b64decode(json_response['threeDSHtmlContent'])
            request.session['threeDSHtmlContent'] = str(secure)
            status = "redirectTo3dSecurity"
            messages.add_message(request, messages.SUCCESS, request.session['threeDSHtmlContent'])
            print(request.session['threeDSHtmlContent'])
            print("-----------", "işlem başarılı")
        else:
            messages.add_message(request, messages.INFO, {'msg': 'failed' + response})
            # if json_response[""]
            print("!!! --- hATA VAR ---", response)

    return status


def secure_view(request):
    secure_code = str(request.session['threeDSHtmlContent'])
    secure_code = secure_code.replace("\\n", "").replace("b'", "").replace("'", "")
    context = {
        'secure_code': secure_code,
    }
    return render(request, 'site/account/checkout/threedsecurity.html', context)


def checkout_done(request):
    options = {
        'api_key': 'sandbox-pN5AwOUOtVHZW6ElUmlwTilUVQDG6ZyX',
        'secret_key': 'sandbox-s80sblJrFDBQqGAKIe2swHkZxAv3BJMH',
        'base_url': iyzipay.base_url
    }
    ssl._create_default_https_context = ssl._create_unverified_context
    if request.method == 'POST':
        if request.POST.get('status') == 'success' and request.POST.get('mdStatus') == '1':
            req = {
                'locale': 'tr',
                'conversationId': request.POST.get('conversationId'),
                'paymentId': request.POST.get('paymentId'),
            }
            if request.POST.get('conversationData'):
                req.update({
                    'conversationData': request.POST.get('conversationData')
                })
            threeds_payment = iyzipay.ThreedsPayment().create(req, options)
            result = threeds_payment.read().decode('utf-8')
            json_response = json.loads(result)
            for res in json_response["itemTransactions"]:
                paytransid = res['paymentTransactionId']
            if json_response['status'] == 'success':
                siparisi_tamamla(request)
                return HttpResponse('işlem başarılı siparişiniz alındı')
            else:
                return HttpResponse('işlem başarısız')
        else:
            return HttpResponse('işlem başarısız')


def siparisi_tamamla(request):
    user_sepet_id = None
    adres_text = None
    product_text = ""
    try:
        mail = request.session.get("mail")
    except:
        mail = None
    if request.session.get("adres_id"):
        adres_id = request.session.get("adres_id")
        adres = Adress.objects.filter(pk=adres_id)
        adres_text = "ŞEHİR : " + str(adres.get().city) + "--İLÇE: " + str(adres.get().province) + "--ADRES : " + (
            adres.get().adres) + "--MÜŞTERİ :" + adres.get().name + " " + adres.get().last_name + "--TELEFON :" + adres.get().phone_number + "  MAİL :" + adres.get().mail + " CARGO :" + str(
            adres.get().cargo)
    if request.session.get("user_basket_id"):
        user_sepet_id = request.session.get("user_basket_id")
        sepet_urunler = SepetUrunler.objects.filter(parent_sepet__id=user_sepet_id)
        for item in sepet_urunler:
            product_text += "[Ürün kodu :" + item.parent_product.code + " Ürün Adı : " + str(item.parent_product.title) + "-- Özellikler : " + str(item.attr) + "--- Adet : " + str(item.qty) + "]---"
    siparis = TamSiparisler.objects.create(user_sepet=Sepet.objects.get(id=user_sepet_id), mail=mail, adres_text=adres_text, product_text=product_text, cargo=Cargo.objects.last())
    if request.user.is_authenticated:
        siparis.user = User.objects.get(id=request.user.id)
    else:
        siparis.user_ip = get_client_ip(request)
    siparis.save()


# account checkout and  address info
def checkout(request):
    form = Adress_Form()
    basket = Sepet.create_or_get_basket(Sepet, request.user, get_client_ip(request))
    request.session["user_basket_id"] = basket.id  # used by taksit_getir
    oldAdres = None
    if request.user.is_authenticated:
        oldAdres = Adress.objects.filter(user__id=request.user.id)
    basket_items = SepetUrunler.get_basket_items(SepetUrunler, basket)
    if request.method == "POST":
        if "adresFormButton" in request.POST:
            adresFormPostForCheckOutView(request, Adress_Form(request.POST), basket, basket_items)
            updateBasket(basket, basket_items)
        else:
            if request.POST.get("selected_adres"):
                if request.POST.get("selected_adres") != "0":
                    adresID = request.POST.get("selected_adres")
                else:
                    adresID = request.session.get("adresID")
            elif request.session.get("adresID"):
                adresID = request.session.get("adresID")
            else:
                if request.user.is_authenticated:
                    adresID = Adress.objects.filter(user__id=request.user.id).last()
                else:
                    adresID = None
            request.session["adresID"] = adresID
            print(adresID)
            if adresID:
                print(adresID)
                Point = collections.namedtuple('Point', ['number', 'holderName', 'expireMonth', 'expireYear', 'CVC'])
                myCard = Point(request.POST.get("cardNumberCre"), request.POST.get("cardHolderName"), request.POST.get("cardMonth"), request.POST.get("cardYear"), request.POST.get("cvc"))

                status = payment(request, basket, basket_items, request.POST.get("taksit_sayisi", 1), adresID, myCard, get_client_ip(request))
                if status == "redirectTo3dSecurity":
                    return HttpResponseRedirect("/kullanici/three-d-security")
            else:
                messages.add_message(request, messages.ERROR, "Geçerli bir adres sağlanamadı")
    context = {
        'form': form,
        'adresler': oldAdres,
        'sepetim': basket_items
    }
    return render(request, "site/account/checkout/checkout.html", context)


def updateBasket(basket, basketItems):
    if basket:
        for item in basketItems:
            details = getDetailListForUpdateCart(item.details)
            discPrice = Campaign.calcDiscountPrice(Campaign, item.parent_product)
            variant = Variant.get_product_variant(Variant, item.parent_product.id, details)
            if variant:
                variantPrice = variant.price
            else:
                variantPrice = 0
            price = (Decimal(item.parent_product.price) - discPrice) + variantPrice
            totalPrice = price * item.qty
            item.price = price
            item.totalPrice = totalPrice
            item.save(update_fields=["price", "totalPrice"])
        Sepet.update_basket(Sepet, basket)


# user Views
def loginView(request):
    """
        Register  and sign view
    """
    loginForm = LoginForm(request.POST or None)
    registerForm = RegisterForm(request.POST or None)
    if request.method == "POST":
        if "login" in request.POST:
            oldBasket = Sepet.create_or_get_basket(Sepet, None, get_client_ip(request))
            isUserLogged = userLogin(request, loginForm)
            if isUserLogged:
                basket = Sepet.create_or_get_basket(Sepet, request.user, get_client_ip(request))
                if oldBasket.basket_have_item(basket):
                    userBasketUpdateAfterUserLogin(request, oldBasket, basket)
        else:
            if registerForm.is_valid():
                userRegister(request, registerForm)
            else:
                messages.add_message(request, messages.WARNING, registerForm.errors)
    context = {
        'loginForm': loginForm,
        'registerForm': registerForm,
    }
    # social media login
    if request.user.is_authenticated:
        user = request.user
        try:
            github_login = user.social_auth.get(provider='github')
        except UserSocialAuth.DoesNotExist:
            github_login = None
        try:
            twitter_login = user.social_auth.get(provider='twitter')
        except UserSocialAuth.DoesNotExist:
            twitter_login = None
        try:
            facebook_login = user.social_auth.get(provider='facebook')
        except UserSocialAuth.DoesNotExist:
            facebook_login = None
        can_disconnect = (user.social_auth.count() > 1 or user.has_usable_password())
        context.update({'github_login': github_login,
                        'twitter_login': twitter_login,
                        'facebook_login': facebook_login,
                        'can_disconnect': can_disconnect})

    return render(request, "site/account/login.html", context)


def logout_view(request):
    logout(request)
    return redirect('accounts:login')


# AJAX METHODS
def update_cart(request):
    qtyList = request.GET.getlist("qtyList[]")
    messages = None;
    basketID = request.GET.get("basketID")
    cargoID = request.GET.get("cargoID")
    for q in qtyList:
        sp_list = str(q).split(",")
        basketItemID = sp_list[0]
        qty = int(sp_list[1])
        if SepetUrunler.objects.filter(id=basketItemID).exists():
            sepetItem = SepetUrunler.objects.get(id=basketItemID)
            messages = checkStockAndSaveForUpdateCart(sepetItem, qty)
    try:
        basket = Sepet.objects.get(id=basketID)
        basket.cargo = Cargo.objects.get(id=cargoID)
        basket.save(update_fields=['cargo'])
        newBasket = serializers.serialize("json", SepetUrunler.get_basket_items(SepetUrunler, basket), fields=['totalPrice', 'priceTotal', 'qty'])
        cartTotal = basket.sepet_tutar
    except:
        newBasket = None
        cartTotal = None
    data = json.dumps({
        'qtyList': qtyList,
        'messages': messages,
        'basket': newBasket,
        'cartTotal': str(cartTotal),
    })
    return HttpResponse(data)


def getDetailListForUpdateCart(sepetItemDetails):
    details = str(sepetItemDetails).replace("[", "").replace("]", "").replace("None", "")
    detailList = []
    for d in details:
        if d != "," and d != "[" and d != " ":
            detailList.append(int(d))
    return detailList


def checkStockAndSaveForUpdateCart(sepetItem, qty):
    sepetItem.qty = qty
    detailList = getDetailListForUpdateCart(sepetItem.details)
    message = None
    variant = None
    indirimTutari = Campaign.calcDiscountPrice(Campaign, sepetItem.parent_product)
    if int(qty) > 0:
        if SepetUrunler.details:
            variant = Variant.get_product_variant(Variant, sepetItem.parent_product.id, detailList)
        if variant:
            if variant.qty >= int(qty):
                basketItemPrice = (Decimal(sepetItem.parent_product.price) + variant.price) - indirimTutari
                sepetItem.price = basketItemPrice
                sepetItem.totalPrice = qty * basketItemPrice
            else:
                message = "%s adet istenilen üründen (%s) yalnızca %s adet var" % (str(qty), variant.product.title, variant.qty)
        else:
            if sepetItem.parent_product.stock >= int(qty):
                basketItemPrice = Decimal(sepetItem.parent_product.price) - indirimTutari
                sepetItem.price = basketItemPrice
                sepetItem.totalPrice = qty * basketItemPrice
            else:
                message = "%s adlı üründen stokta yalnızca %s adet var. (istenilen adet = )" % (sepetItem.parent_product.title, sepetItem.parent_product.stock, qty)
        if not message:
            sepetItem.save(update_fields=["qty", "price", "totalPrice"])
            Sepet.update_basket(Sepet, Sepet.objects.get(id=sepetItem.parent_sepet.id))
    return message


# AJAX METHOD END


def sepetim(request):
    basket = Sepet.create_or_get_basket(Sepet, request.user, get_client_ip(request))
    basket_items = SepetUrunler.get_basket_items(SepetUrunler, basket)
    updateBasket(basket, basket_items)
    basket_total = 0
    for b in basket_items:
        basket_total += b.totalPrice
    if basket.coupon:
        coupon = Coupon.getCoupon(Coupon, basket.coupon.code)
    else:
        coupon = None
    context = {
        'sepetim': basket_items,
        'basketTotal': basket_total,
        'cargos': Cargo.objects.all(),
        'coupon': coupon,
    }
    return render(request, "site/account/sepetim.html", context)


def favorilerim(request):
    if request.user.is_authenticated:
        user = User.objects.get(pk=request.user.id)
        favList = Product.objects.filter(id__in=Favorites.objects.filter(user=request.user).values('fav_p'))
    else:
        favList = None
        user = None
    context = {
        'user': user,
        'favList': favList,
    }
    return render(request, "site/account/favorilerim.html", context)


@login_required  # ---> kullanılmıyor olabilir
def settings(request):
    user = request.user

    try:
        github_login = user.social_auth.get(provider='github')
    except UserSocialAuth.DoesNotExist:
        github_login = None

    try:
        twitter_login = user.social_auth.get(provider='twitter')
    except UserSocialAuth.DoesNotExist:
        twitter_login = None

    try:
        facebook_login = user.social_auth.get(provider='facebook')
    except UserSocialAuth.DoesNotExist:
        facebook_login = None

    can_disconnect = (user.social_auth.count() > 1 or user.has_usable_password())

    return render(request, 'registration/settings.html', {
        'github_login': github_login,
        'twitter_login': twitter_login,
        'facebook_login': facebook_login,
        'can_disconnect': can_disconnect
    })


@login_required
def password(request):
    if request.user.has_usable_password():
        PasswordForm = PasswordChangeForm
    else:
        PasswordForm = AdminPasswordChangeForm

    if request.method == 'POST':
        form = PasswordForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Parolan başarıyla güncellendi')
            return redirect('accounts:password')
        else:
            messages.error(request, 'Lütfen aşağıdaki hataları düzeltin')
    else:
        form = PasswordForm(request.user)
    return render(request, 'registration/password.html', {'form': form})
