from django.db import models
from django.utils.crypto import get_random_string
from smart_selects.form_fields import ChainedManyToManyField

from home.models import AnaMenu, AltMenu
import uuid, re
from django.db.models.signals import pre_save
from django.utils.text import slugify
from django.dispatch import receiver
from smart_selects.db_fields import ChainedForeignKey
from ckeditor.fields import RichTextField
from campaings.models import Campaign
from django.urls import reverse


class SubDetail(models.Model):
    title = models.CharField(max_length=50, verbose_name="Başlık")
    # product = models.ForeignKey('Product', on_delete=models.CASCADE)
    sub_detail = models.ForeignKey('product.Detail', on_delete=models.CASCADE, null=True, blank=True, verbose_name="Alt Detay")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Ürün Alt Detay"
        verbose_name_plural = "Ürün Alt Detayları"


class Attribute(models.Model):
    name = models.CharField(max_length=300, verbose_name="Başlık")

    def __str__(self):
        return self.name

    def getAttr(self, products):
        attr = Attribute.objects.filter(id__in=Detail.objects.filter(product__in=products).values("parent_attr__id"))
        return attr

    class Meta:
        verbose_name = "Özellik"
        verbose_name_plural = "Özellikler"


class Sub_Attr(models.Model):
    parent = models.ForeignKey(Attribute, on_delete=models.CASCADE, verbose_name="Üst Özellik")
    title = models.CharField(max_length=50, verbose_name="Başlık")

    def __str__(self):
        return self.title

    def getSubAttr(self, products):
        subAttr = Sub_Attr.objects.filter(id__in=Detail.objects.filter(product__in=products).values("sub_attr__id"),
                                          parent__in=Attribute.objects.filter(
                                              id__in=Detail.objects.filter(product__in=products).values("parent_attr__id")))
        return subAttr

    class Meta:
        verbose_name = "Alt Özellik"
        verbose_name_plural = "Alt Özellikler"


class Detail(models.Model):
    product = models.ForeignKey('product.Product', on_delete=models.CASCADE, verbose_name="Ürün")
    parent_attr = models.ForeignKey('product.Attribute', on_delete=models.CASCADE, verbose_name="Üst Özellik")
    # sub_attr = models.ManyToManyField('product.Sub_Attr', null=True, blank=True)
    sub_attr = ChainedManyToManyField(
        Sub_Attr,
        chained_field="parent_attr",
        chained_model_field="parent", verbose_name="Alt Özellikler")

    def __str__(self):
        return str(self.parent_attr)

    class Meta:
        verbose_name = "Ürün Detay"
        verbose_name_plural = "Ürün Alt Detayları"


class Variant(models.Model):
    product = models.ForeignKey('product.Product', on_delete=models.CASCADE, null=True, blank=True)
    sub_details = models.ManyToManyField('product.Sub_Attr')
    price = models.SmallIntegerField()
    qty = models.SmallIntegerField()

    def __str__(self):
        return str(self.product)

    def get_product_variant(self, product_id, choices):
        variant = Variant.objects.filter(product__pk=product_id)
        for item in range(len(choices)):
            variant = variant.filter(sub_details__pk=choices[item])
        if variant:
            variant = Variant.objects.get(id=variant.get().id)
        else:
            variant = None
        return variant


class Product(models.Model):
    main_menu = models.ForeignKey('home.AnaMenu', on_delete=models.CASCADE)
    sub_menu = ChainedForeignKey('home.AltMenu', chained_field='main_menu', chained_model_field='parent')
    title = models.CharField(max_length=150, verbose_name="Ürün Adı")
    # detail = models.TextField()
    info = RichTextField()
    code = models.CharField(max_length=150, default=get_random_string(allowed_chars="1234567890", length=6), editable=False, verbose_name="Ürün Kodu")
    brand = models.ForeignKey('product.Brands', on_delete=models.CASCADE)
    price = models.DecimalField(decimal_places=2, max_digits=20, default=0)
    date = models.DateTimeField(auto_now_add=True)
    stock = models.IntegerField()
    active = models.BooleanField(default=True)
    slug = models.SlugField(verbose_name='link', unique=True)
    image = models.ImageField(upload_to="product", verbose_name="Ana Resim")
    tags = models.CharField(max_length=200, help_text="Lütfen kelimelerin arasında virgül kullanınız ve boşluk kullanmayınız", null=True, blank=True)
    disc_price = models.DecimalField(decimal_places=2, max_digits=20, verbose_name="İndirimli Fiyat", help_text="İndirim eklemek istemiyorsanız boş kalsın", null=True, blank=True)
    disc_group = models.ForeignKey(Campaign, on_delete=None, null=True, blank=True, default=0)
    voteAverage = models.DecimalField(decimal_places=2, max_digits=4, default=0)

    def __str__(self):
        return self.title

    def tags_split(self):
        if self.tags:
            return self.tags.split(',')
        return None

    def get_url(self):
        return reverse("shop:product_detail", kwargs={'category': self.main_menu.slug, 'product': self.slug})

    def relatedProducts(self, adet, subCategorySlug, selfID):
        return self.objects.filter(active=True, sub_menu__slug=subCategorySlug).exclude(id=selfID)[:adet]

    def latestProductsMainCat(self, adet, main_category):
        product_list = Product.objects.filter(active=True, main_menu__slug=main_category)[:adet].values("id", "title", "slug", "image", "price", "main_menu__title", "main_menu__slug")
        return product_list

    def onerilenler(self, slug):
        products = Product.objects.filter(active=True, sub_menu__slug=slug).values("price", "title", "image", "slug", "main_menu__title", "main_menu__slug", "image")
        return products

    def mostVotedOnCategory(self, categorySlug, adet):
        return self.objects.filter(active=True, main_menu__slug=categorySlug).order_by("-voteAverage")[:adet].values("title", "image", "slug", "price", "main_menu__slug", "main_menu__title")

    def has_stock(self, product_id, adet, variants):
        variant_stock = Variant.get_product_variant(Variant, product_id, variants)
        if variant_stock:
            variant_stock = variant_stock.qty
        else:
            variant_stock = 0
        urun = Product.objects.filter(id=product_id)
        if urun:
            if variant_stock != 0:
                if variant_stock >= int(adet):
                    return True
            else:
                if urun.get().stock >= int(adet):
                    return True
        return False


@receiver(pre_save, sender=Product)
def productTags(sender, instance, *args, **kwargs):
    if not type(instance.tags) == list and instance.tags:
        instance.tags = instance.tags.lower()
        instance.tags = ClearTRChars(instance.tags)
        if instance.tags.startswith(',,') or instance.tags.endswith(',,'):
            instance.tags = instance.tags.replace(',,', "")
        if not (instance.tags.startswith(',') and instance.tags.endswith(',')):
            instance.tags = ('%s%s%s' % (",", instance.tags, ","))
        instance.tags = instance.tags.replace(",,", ",");
        instance.tags = re.sub('[^.,a-zA-Z ]', '', instance.tags)


def ClearTRChars(text):
    return text.replace("ı", "i").replace("ü", "u").replace("ç", "c").replace("ş", "s").replace("ğ", "g").replace("ö", "o").replace("ş", 's')


@receiver(pre_save, sender=Product)
def product_slug(sender, instance, *args, **kwargs):
    if instance.sub_menu:
        instance.slug = slugify('%s-%s' % (instance.sub_menu.slug, instance.title))
    else:
        instance.slug = slugify('%s-%s' % (instance.main_menu.slug, instance.title))
    unique_slug = instance.slug
    counter = 1
    while Product.objects.filter(slug=unique_slug).exclude(id=instance.id).exists():
        if not instance.sub_menu:
            unique_slug = '{}-{}-{}'.format(instance.main_menu.slug, slugify(instance.title), counter)
        else:
            unique_slug = '{}-{}-{}'.format(instance.sub_menu.slug, slugify(instance.title), counter)
        counter += 1
    instance.slug = unique_slug


class Brands(models.Model):
    title = models.CharField(max_length=100)
    desc = models.CharField(max_length=150)
    image = models.ImageField(upload_to="brands", blank=True)

    def __str__(self):
        return self.title

    def getBrandsInProducts(self, products):
        return Brands.objects.filter(id__in=products).values("title", "id")


class Files(models.Model):
    parent = models.ForeignKey('product.Product', on_delete=models.CASCADE)
    title = models.CharField(max_length=100, verbose_name="Dosya Başlık")
    image = models.ImageField(upload_to="product")

    def __str__(self):
        return self.title

    def getFilesProduct(self, productID):
        return Files.objects.filter(parent__id=productID)
