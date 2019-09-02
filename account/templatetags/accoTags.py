from django import template
from campaings.models import Campaign
from decimal import Decimal
from account.models import Sepet, Coupon

register = template.Library()


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@register.filter
def getDiscPrice(product):
    discPrice = Campaign.calcDiscountPrice(Campaign, product)
    return discPrice


@register.filter
def cikarDecimalPrice(self, price):
    return Decimal(self) - Decimal(price)


@register.filter
def addDecimalPrice(self, price):
    return round(Decimal(self) + Decimal(price), 2)


@register.filter
def getCouponDiscPrice(self):
    try:
        coup = Coupon.getCoupon(Coupon, self)
        return coup.disc_price
    except:
        return 0
