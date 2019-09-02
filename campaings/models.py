from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.text import slugify
from decimal import Decimal
from django.utils import timezone
from django.urls import reverse


class Campaign(models.Model):
    title = models.CharField(max_length=100, verbose_name="Kampanya Adı")
    discPercentage = models.SmallIntegerField(default=0, validators=[MaxValueValidator(100), MinValueValidator(1)], help_text="İndirim Yüzdesi")
    slug = models.SlugField(unique=True, verbose_name="Url")
    active = models.BooleanField(default=False)
    start_date = models.DateTimeField(verbose_name="Kampanya Başlangıç")
    last_date = models.DateTimeField(verbose_name="Kampanya bitiş")
    banner = models.ImageField(upload_to="campaignBanner", null=True, blank=True)

    def __str__(self):
        return self.title

    def calcDiscountPrice(self, product):
        discount = product.disc_price
        if discount:
            discPrice = Decimal(product.price) - Decimal(discount)
        elif product.disc_group:
            camp = Campaign.objects.filter(id=product.disc_group.id, last_date__gte=timezone.now(), start_date__lte=timezone.now(), active=True)
            if camp:
                discPrice = (Decimal(product.price) * Decimal(product.disc_group.discPercentage)) / 100
            else:
                discPrice = 0
        else:
            discPrice = 0
        return discPrice

    def getProDiscedPrice(self, productID):
        from django.apps import apps
        myProduct = apps.get_model('product', 'Product')
        product = myProduct.objects.get(pk=productID)
        print("product", product, "id : ", productID)
        if product:
            discPrice = Campaign.calcDiscountPrice(self, product)
            if not discPrice == 0:
                proPrice = Decimal(product.price) - Decimal(discPrice)
                return proPrice
        return 0

    def getActiveCamp(self):
        return Campaign.objects.filter(active=True, last_date__gte=timezone.now(), start_date__lte=timezone.now())

    def getCamp(self, campID):
        try:
            return self.objects.get(active=True, last_date__gte=timezone.now(), start_date__lte=timezone.now(), id=campID)
        except:
            return None

    def getUrl(self):
        return reverse("campaign:campProList", kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        self.slug = slugify(self.replaceTRChars(self.title))
        return super(Campaign, self).save(*args, **kwargs)

    def replaceTRChars(self, value):
        value = str(value).replace("ğ", "g").replace("ü", "u").replace("ı", "i").replace("ş", "s").replace("ö", "o").replace("ç", "c")
        return value
