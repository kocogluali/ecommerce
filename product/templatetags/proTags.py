from django import template
from home.models import AltMenu, AnaMenu
from product.models import Product
from campaings.models import Campaign

register = template.Library()


def showLeftCategorySidebar(category):
    subMenus = AltMenu.objects.filter(active=True, parent__slug=category)
    otherCat = AnaMenu.get_all_cats(AnaMenu)
    return {'subMenus': subMenus, 'otherCat': otherCat}


register.inclusion_tag("site/product/templatetags/leftCategorySidebar.html")(showLeftCategorySidebar)


# filter sub attr in main attr
@register.filter
def filterSubAttr(self, mainCat):
    subAttr = self.filter(parent__id=mainCat)
    return subAttr


# COMMENTS
@register.filter()
def multiply(value, arg):
    return value * arg


@register.filter()
def commentCount(self, number):
    return self.filter(votes=number).count()


@register.filter()
def calcCommentAverage(self, value):
    toplam = 0
    for v in value:
        toplam += v.votes
    try:
        ort = round(toplam / value.count(), 1)
    except:
        ort = 0
    return ort


@register.filter()
def calcCommentPercent(self, comments):
    adet = commentCount(self, comments)
    toplamAdet = self.count()
    try:
        result = round(adet * 100 / toplamAdet)
    except:
        result = 0
    return result


@register.filter()
def calcDiscountPrice(self, discountPercent):
    price = (self * (100 - int(discountPercent))) / 100
    return price


@register.filter
def getProDiscedPricebyProID(proID):
    discedProPrice = Campaign.getProDiscedPrice(Campaign, proID)
    return discedProPrice
