from django import template
from home.models import AnaMenu, AltMenu
from account.models import SepetUrunler, Sepet
from account.templatetags.accoTags import get_client_ip
from account.views import getDetailListForUpdateCart
from product.models import Variant
from campaings.models import Campaign
from decimal import Decimal
from ayarlar.models import SiteSettings

register = template.Library()


@register.simple_tag
def showHeaderIndex(request):
    MainMenu = AnaMenu.objects.filter(active=True)
    SubMenu = AltMenu.objects.filter(active=True)
    site = SiteSettings.getConfig(SiteSettings)
    basketItems = SepetUrunler.objects.filter(parent_sepet=Sepet.create_or_get_basket(Sepet, request.user, get_client_ip(request)))
    return {'MainMenu': MainMenu, 'SubMenu': SubMenu, 'basketItems': basketItems, 'camps': Campaign.getActiveCamp(Campaign), 'site': site}


register.inclusion_tag("site/base/header/headerIndex.html")(showHeaderIndex)


@register.simple_tag
def showHeaderForAll(request):
    MainMenu = AnaMenu.objects.filter(active=True)
    SubMenu = AltMenu.objects.filter(active=True)
    site = SiteSettings.getConfig(SiteSettings)
    basketItems = SepetUrunler.objects.filter(parent_sepet=Sepet.create_or_get_basket(Sepet, request.user, get_client_ip(request)))
    return {'MainMenu': MainMenu, 'SubMenu': SubMenu, 'basketItems': basketItems, 'camps': Campaign.getActiveCamp(Campaign), 'site': site}


register.inclusion_tag("site/base/header/headerAll.html")(showHeaderForAll)


@register.simple_tag
def showFooter():
    site = SiteSettings.getConfig(SiteSettings)
    cats = AnaMenu.objects.filter(active=True).values("title", "slug")
    return {'site': site, 'cats': cats}


register.inclusion_tag("site/base/footer.html")(showFooter)


@register.filter
def filterSubAttr(self, mainCat):
    subAttr = self.filter(parent__id=mainCat)
    return subAttr


@register.filter
def get_product_variant(self, arguman):
    product_id = self
    choices = getDetailListForUpdateCart(arguman)
    variant = Variant.objects.filter(product__pk=product_id)
    for item in range(len(choices)):
        variant = variant.filter(sub_details__pk=choices[item])
    print("new item")
    if variant:
        variant = Decimal(Variant.objects.get(id=variant.get().id).price)
    else:
        variant = Decimal(0)
    return variant

# @register.filter
# def addDecimalVariant(self, value):
#     revalue = Decimal(self) + Decimal(value)
#     return revalue
