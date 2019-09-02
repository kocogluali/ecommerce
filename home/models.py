from django.db import models
from django.template.defaultfilters import slugify


class AnaMenu(models.Model):
    title = models.CharField(max_length=120, verbose_name='Menü başlık')
    slug = models.SlugField(unique=True, verbose_name='link')
    active = models.BooleanField(default=True)
    banner = models.ImageField(upload_to="menu_banner")

    class Meta:
        verbose_name_plural = "Ana Menüler"

    def __str__(self):
        return self.slug

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title.replace('ı', 'i'))
        return super(AnaMenu, self).save(*args, **kwargs)

    def otherMainCats(self, extendCatSlug):
        return AnaMenu.objects.filter(active=True).exclude(slug=extendCatSlug)

    def get_all_cats(self):
        return self.objects.filter(active=True)


class AltMenu(models.Model):
    parent = models.ForeignKey('AnaMenu', on_delete=models.CASCADE)
    title = models.CharField(max_length=120, verbose_name='Menü başlık')
    slug = models.SlugField(unique=True, verbose_name='link', null=True, blank=True)
    active = models.BooleanField(default=True)
    banner = models.ImageField(upload_to="menu_banner", null=True, blank=True)

    class Meta:
        verbose_name_plural = "Alt Menüler"

    HOT = 'HOT'
    NEW = 'NEW'
    SALE = 'SALE'
    LABEL_TYPES = (
        (HOT, 'HOT'),
        (NEW, 'NEW'),
        (SALE, 'SALE'),
    )
    label_types = models.CharField(max_length=12, choices=LABEL_TYPES, verbose_name='Etiket', null=True, blank=True, )

    def is_upperclass(self):
        return self.label_types in (self.NEW, self.SALE)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = "%s-%s" % (slugify(self.parent.slug), slugify(self.title))
        return super(AltMenu, self).save(*args, **kwargs)


class Banner(models.Model):
    slogan = models.CharField(max_length=150)
    sub_slogan = models.CharField(max_length=150, verbose_name="Alt slogan")
    image = models.ImageField(upload_to="banner", verbose_name='Banner')
    active = models.BooleanField(default=True)
    url = models.CharField(max_length=200, verbose_name="Hedef Url", null=True, blank=True)

    def __str__(self):
        return self.slogan
