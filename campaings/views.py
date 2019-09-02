from django.shortcuts import render
from .models import *
from django.shortcuts import get_object_or_404
from product.models import Product
from product.views import sayfalama
from home.views import orderByProduct


def campProductList(request, slug):
    campaign = get_object_or_404(Campaign, slug=slug)
    products = Product.objects.filter(disc_group__id=campaign.id)
    curPage = request.GET.get("sayfa", 1)
    try:
        perPageItem = int(request.GET.get("ppp"))
    except:
        perPageItem = 3
    products = orderByProduct(request.GET.get("orderby"), products)
    mvp = sayfalama(request, products, perPageItem, curPage)
    context = {
        'camps': campaign,
        'products': mvp,
    }
    return render(request, "site/campaign/campProductList.html", context)
