from django.shortcuts import render, get_object_or_404
from .models import Product
from home.models import AnaMenu, AltMenu
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Attribute, Sub_Attr, Detail, Brands, Files, Variant
from comment.models import ProductsComments
from django.contrib import messages
from django.core import serializers
import json, datetime, math
from decimal import Decimal
from django.http import HttpResponse
from django.db.models import Q
from account.models import Sepet, SepetUrunler
from account.templatetags.accoTags import get_client_ip
from campaings.models import Campaign
from home.views import filterByPrice, orderByProduct


# AJAX // JSON
def product_filter(request):
    price_min = request.GET.get("price_min")
    price_max = request.GET.get("price_max")
    slug = request.GET.get("slug")
    secimler = request.GET.getlist('secimler[]')
    page = int(request.GET.get("page"))
    perPageItem = int(request.GET.get("perPageItem"))
    brandss = request.GET.getlist("brandss[]")
    orderType = request.GET.get("orderBy")
    if AltMenu.objects.filter(slug=slug).exists():
        product = Product.objects.filter(sub_menu__slug=slug, active=True)
    else:
        return render(request, '404.html')
    product = filterByPrice(product, price_min, price_max, brandss)
    product = orderByProduct(orderType, product)
    for s in secimler:
        if s:
            filterList = []
            for sin in str(s).split(","):
                filterList.append(int(sin))
            product = product.filter(id__in=Detail.objects.filter(sub_attr__id__in=filterList).values("product__id")).distinct()
    gelen_sublar = Sub_Attr.objects.filter(id__in=Detail.objects.filter(product__in=product).values("sub_attr__id"),
                                           parent__in=Attribute.objects.filter(
                                               id__in=Detail.objects.filter(product__in=product).values("parent_attr__id"))).distinct()
    gelen_brands = Brands.objects.filter(id__in=product.values("brand__id"))
    filterSideBarAttr = Attribute.objects.filter(id__in=Detail.objects.filter(product__in=product).values("parent_attr__id").distinct())
    myp = sayfalama(request, product, perPageItem, page)
    myp = serializers.serialize("json", myp, fields=("title", "price", "slug", "info", "image", "voteAverage","code"))
    gelen_brands = serializers.serialize("json", gelen_brands, fields=('id', 'title'))
    gelen_sublar = serializers.serialize("json", gelen_sublar, fields=('id', 'title', 'parent'))
    filterSideBarAttr = serializers.serialize("json", filterSideBarAttr, fields=('id', 'name'))
    if math.ceil(product.count() / perPageItem) == 0:
        sayfa_sayim = 1
    else:
        sayfa_sayim = math.ceil(product.count() / perPageItem)
    data = json.dumps({
        'products': myp,
        'p_count': product.count(),
        'sayfa_sayisi': sayfa_sayim,
        'perPageItem': perPageItem,
        'gelen_sublar': gelen_sublar,
        'gelen_brands': gelen_brands,
        'filterSideBarAttr': filterSideBarAttr,
    })
    return HttpResponse(data)


# END AJAX / JSON


def product_list(request, slug):
    template = "site/product/ProductList.html"
    context = {}
    mainCat = AnaMenu.objects.filter(slug=slug, active=True)
    if mainCat:  # filter in main Category
        template = "site/product/category/allProductCategory.html"
        latestProduct = Product.latestProductsMainCat(Product, 5, slug)
        subMenus = AltMenu.objects.filter(active=True, parent__slug=slug)
        mostVoted = Product.mostVotedOnCategory(Product, slug, 15)
        context.update({'latestProduct': latestProduct, 'subMenus': subMenus, 'mostVoted': mostVoted})
        product_category(request, slug)
    else:
        content = Product.objects.filter(sub_menu__slug=slug, active=True).order_by(
            "-id")  # values("title", "slug", "image", "main_menu__title", "sub_menu__title", "price", "sub_menu__slug", "code", "main_menu__slug", "info", "stock")
        if not content:
            raise Http404("Herhangi bir Sayfa Bulunuamadı")
        attr = Attribute.getAttr(Attribute, content)
        subAttr = Sub_Attr.getSubAttr(Sub_Attr, content)
        brands = Brands.getBrandsInProducts(Brands, content.values("brand__id"))
        proCount = content.count()
        content = sayfalama(request, content, 3, 1)
        onerilenUrunler = Product.onerilenler(Product, slug)
        lastProduct = Product.latestProductsMainCat(Product, 3, content[0].main_menu.slug)
        context.update(
            {'products': content, 'oneriler': onerilenUrunler, 'attr': attr, 'subAttr': subAttr, 'brands': brands, 'proCount': proCount, 'lastProduct': lastProduct})
    return render(request, template, context=context)


def product_category(request, slug):
    template = "site/product/category/allProductCategory.html"
    content = AltMenu.objects.filter(active=True, parent__slug=slug)
    context = {
        'content': content
    }
    return render(request, template, context=context)


def product_detail(request, category, product):
    urun = get_object_or_404(Product, active=True, slug=product, main_menu__slug=category)
    discPrice = Decimal(urun.price) - Decimal(Campaign.calcDiscountPrice(Campaign, urun))
    urun_detaylar = Detail.objects.filter(product=urun)
    gallery = Files.getFilesProduct(Files, urun.id)
    relatedPro = Product.relatedProducts(Product, 8, urun.sub_menu.slug, urun.id)
    comments = ProductsComments.objects.filter(product__id=urun.id, active=True)
    camp = None
    if urun.disc_group:
        camp = Campaign.getCamp(Campaign, urun.disc_group.id)
    if request.method == "POST":
        if 'yorum_ekle' in request.POST:
            yorumEkle(request, urun)
        else:
            selected_details = []
            strVariantAttr = ""
            postQty = request.POST.get("qty", 1)
            for detay in urun_detaylar:
                if request.POST.get('selvaryant' + str(detay.id) + ''):
                    selected_details.append(int((request.POST.get('selvaryant' + str(detay.id) + ''))))
                    strVariantAttr += "%s : %s    " % (detay.parent_attr.name, Sub_Attr.objects.get(id=request.POST.get("selvaryant" + str(detay.id) + "")).title)
            if not SepetUrunler.has_product(SepetUrunler, Sepet.create_or_get_basket(Sepet, request.user, get_client_ip(request)), urun, selected_details, strVariantAttr):
                if Product.has_stock(Product, urun.id, postQty, selected_details):
                    basket_add_product(request, urun, postQty, strVariantAttr, selected_details)
                else:
                    messages.add_message(request, messages.INFO, "Stokta Yeterli Sayıda Ürün Yok")
            else:
                messages.add_message(request, messages.INFO, "Bu ürün daha önceden sepetinize eklenmiş. Sepetim Kısmından Adet Sayısını Güncelleyebilirsin")

    context = {
        'urun': urun,
        'attr': urun_detaylar,
        'gallery': gallery,
        'comments': comments,
        'discPrice': discPrice,
        'relatedPro': relatedPro,
        'camp': camp,
    }
    return render(request, "site/product/productDetail.html", context)


def sayfalama(request, content, perPageItem, page):
    paginator = Paginator(content, perPageItem)
    try:
        content = paginator.page(page)
    except PageNotAnInteger:
        content = paginator.page(1)
    except EmptyPage:
        content = paginator.page(paginator.num_pages)
    return content


def yorumEkle(request, urun):
    yorum = ProductsComments.addComment(ProductsComments, request.user, urun, request.POST.get("comment"), votes=request.POST.get("votes"))
    if yorum:
        messages.add_message(request, messages.SUCCESS, "Yorum eklendi yönetici onayından sonra burada görebilirsiniz")
    else:
        messages.add_message(request, messages.ERROR, "Yorum eklenirken hata oluştu")


def basket_add_product(request, urun, qty, attrText, selected_details):
    basket = Sepet.create_or_get_basket(Sepet, request.user, get_client_ip(request))
    # print(basket)
    basket_item = SepetUrunler.add_product(SepetUrunler, urun, qty, attrText, basket, selected_details)
    if basket_item:
        messages.add_message(request, messages.SUCCESS, "Ürün Sepetinize Eklendi")
    else:
        messages.add_message(request, messages.ERROR, "Ürün Sepete Eklenirken Hata Oluştu")


def urun_fiyat_getir(request):  # AJAX METHOD
    product_id = int(request.GET.get('product_id'))
    secimler = request.GET.getlist('secimler[]')
    post_product = Product.objects.get(pk=product_id)
    varyant = Variant.objects.filter(product__pk=product_id)
    indirimTutari = Campaign.calcDiscountPrice(Campaign, post_product)
    for item in range(len(secimler)):
        varyant = varyant.filter(sub_details__pk=secimler[item])
    try:
        vary_stok = varyant.get().qty
    except:
        vary_stok = post_product.stock
    try:
        var_price = Decimal(varyant.get().price + post_product.price) - indirimTutari
    except:
        var_price = Decimal(post_product.price) - indirimTutari
    # varyant = serializers.serialize("json", varyant,fields=('price',))
    data = json.dumps({
        'total': str(var_price),
        'normal_price': str(var_price + indirimTutari),
        'qty': vary_stok,
    })
    return HttpResponse(data)
