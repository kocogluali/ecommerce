from django.shortcuts import render, redirect
from product.models import Product, Brands
from home.models import AnaMenu, AltMenu
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core import serializers
import json, math
from django.http import HttpResponse
from home.models import Banner
from faq.models import SSS


def homeView(request):
    banner = Banner.objects.filter()
    context = {'banners': banner}
    return render(request, 'site/index.html', context)


def hakkimizda(request):
    return render(request, 'site/home/hakkimizda.html')


def sss(request):
    context = {
        'sss': SSS.objects.filter(active=True)
    }
    return render(request, 'site/home/sss.html', context)


def searchView(request):
    page = request.GET.get('sayfa', 1)
    pageCount = 3  # request.GET.get('pageCount', 1)
    productCat = request.GET.get("product_cat")
    post_type = request.GET.get("post_type")
    query = request.GET.get("q")
    if query:
        products = None
        if query and productCat and post_type == "product":
            if productCat == "0":
                searchMainCat = AnaMenu.objects.filter(active=True)
            else:
                searchMainCat = AnaMenu.objects.filter(slug=productCat, active=True)
            products = Product.objects.filter(Q(title__icontains=query) | Q(info__icontains=query) | Q(code__icontains=query), active=True, main_menu__in=searchMainCat).order_by("-id")
        cats = AnaMenu.objects.filter(active=True)
        subCats = AltMenu.objects.filter(active=True)
        if products:
            brands = Brands.getBrandsInProducts(Brands, products.values("brand__id"))
            totalPageCount = round(products.count() / pageCount)
            proCount = products.count()
        else:
            proCount = None
            brands = None
            totalPageCount = None

        products = sayfalama(request, products, page, pageCount)
        context = {
            'cats': cats,
            'subCats': subCats,
            'proCount': proCount,
            'products': products,
            'pageCount': totalPageCount,
            'brands': brands,
        }
    else:
        context = {}
    return render(request, "site/home/search.html", context)


def sayfalama(request, content, curPage, perPageItem):
    paginator = Paginator(content, perPageItem)
    try:
        content = paginator.page(curPage)
    except PageNotAnInteger:
        content = paginator.page(1)
    except EmptyPage:
        content = paginator.page(paginator.num_pages)
    return content


# AJAX REQUEST
def filterSearchProduct(request):
    price_min = request.GET.get("price_min")
    price_max = request.GET.get("price_max")
    query = request.GET.get("query")
    curPage = request.GET.get("page")
    product_cat = request.GET.get("product_cat")
    perPageItem = int(request.GET.get("perPageItem"))
    ordering = request.GET.get("orderBy")
    brands = request.GET.getlist("brands[]")
    if product_cat == "0":
        mainMenu = AnaMenu.objects.filter(active=True).values("id")
    else:
        mainMenu = AnaMenu.objects.filter(active=True, slug=product_cat)
        # return render(request, '404.html')
    product = Product.objects.filter(Q(title__icontains=query) | Q(info__icontains=query) | Q(code__icontains=query), active=True, main_menu__id__in=mainMenu).order_by("-id")
    product = filterByPrice(product, price_min, price_max, brands)
    myp = orderByProduct(ordering, product)
    myp = sayfalama(request, myp, curPage, perPageItem)
    myp = serializers.serialize("json", myp, fields=("title", "price", "slug", "info", "image", "main_menu__slug", "voteAverage"))
    if math.ceil(product.count() / perPageItem) == 0:
        sayfa_sayim = 1
    else:
        sayfa_sayim = math.ceil(product.count() / perPageItem)
    data = json.dumps({
        'products': myp,
        'p_count': product.count(),
        'sayfa_sayisi': sayfa_sayim,
        'perPageItem': perPageItem,
    })
    return HttpResponse(data)


# AJAX REQUEST END
def replaceTRChars(value):
    value = str(value).replace("ğ", "g").replace("ü", "u").replace("ı", "i").replace("ş", "s").replace("ö", "o").replace("ç", "c")
    return value


def filterByPrice(product_list, price_min, price_max, brands):
    if price_min and price_max:
        product_list = product_list.filter(price__range=(price_min, price_max))
    elif price_max:
        product_list = product_list.filter(price__range=(0, price_max))
    elif price_min:
        product_list = product_list.filter(price__range=(price_min, 99999999))
    if brands:
        product_list = product_list.filter(brand__in=brands)
    return product_list


def orderByProduct(orderingType, product):
    if orderingType == "popularity":
        reProduct = product.order_by("-voteAverage")
    elif orderingType == "date":
        reProduct = product.order_by("-date")
    elif orderingType == "price":
        reProduct = product.order_by("price")
    elif orderingType == "price-desc":
        reProduct = product.order_by("-price")
    else:
        reProduct = product.order_by("-id")
    return reProduct
