from django.db import models
from django.contrib.auth.models import User
import os
from django.core.files.storage import FileSystemStorage

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
upload_storage = FileSystemStorage(location=BASE_DIR, base_url=BASE_DIR)


class SiteSettings(models.Model):
    title = models.CharField(max_length=50)
    desc = models.TextField()
    domain = models.CharField(max_length=70)
    logo = models.ImageField(upload_to="site")
    logo_nav = models.ImageField(upload_to="site")
    icon = models.ImageField(upload_to="site")
    keywords = models.CharField(max_length=150)
    post_detail = models.SmallIntegerField(help_text="Haber detayında sayfa başına düşen karakter sayısı örn:1000",
                                           verbose_name="Haber Detay Karakter", default=1000)
    page_size = models.SmallIntegerField(help_text="Sayfa başına düşen haber sayısı", verbose_name="Haber Sayısı", default=5)
    facebook = models.CharField(max_length=100, default="0")
    twitter = models.CharField(max_length=100, default="0")
    instagram = models.CharField(max_length=100, default="0")
    linkedin = models.CharField(max_length=100, default="0")
    pinterest = models.CharField(max_length=100, default="0")
    youtube = models.CharField(max_length=100, default="0")
    google_plus = models.CharField(max_length=100, default="0")
    tumblr = models.CharField(max_length=100, default="0")
    footer_text = models.CharField(max_length=250)
    top_banner = models.ImageField(upload_to="site", null=True, blank=True)
    iyzi_api = models.CharField(max_length=250, verbose_name="İyzi api key", help_text="İyzico api key", blank=True)
    iyzi_secret_key = models.CharField(max_length=250, verbose_name="İyzico secret key", help_text="İyzico secret key", blank=True)
    gmap = models.TextField(verbose_name="Google Map Link")
    gapi_key = models.CharField(max_length=100)
    view_id = models.CharField(max_length=100)
    jsonFile = models.FileField(upload_to="newsadmin/analitik/", storage=upload_storage, null=True, blank=True)
    phone = models.CharField(max_length=20,verbose_name="Telefon Numarası")
    adres = models.TextField()
    mail = models.CharField(max_length=100,verbose_name="E-mail Adresiniz")

    def __str__(self):
        return self.title

    def f(instance, filename):
        ext = filename.split('.')[-1]
        if instance.pk:
            return '{}.{}'.format(instance.pk, ext)
        else:
            pass

    def getConfig(self):
        config = SiteSettings.objects.last()
        return config

    class Meta:
        verbose_name = "Site Ayar"
        verbose_name_plural = "Site Ayarları"


class Moduller(models.Model):
    title = models.PositiveSmallIntegerField(choices=[(1, 'Banner Yönetimi'), (2, 'Foto Galeri Yönetimi'), (3, 'Haber Yönetimi'), (4, 'İçerik  Yönetimi'), (5, 'Ürün Yönetimi'), (6, 'Referans Yönetimi'), (7, 'Video Galeri Yönetimi')],
                                             verbose_name='Modül Adı', )
    banner = models.CharField(max_length=50, verbose_name="Fotoğraf boyutları", help_text="Banner boyutlarını 600x400 şeklinde giriniz.")
    durum = models.BooleanField(default=True)

    def __str__(self):
        return self.getTitle()

    def getHelpText(self):
        return "Fotoğraf boyutlarını {0} olarak yükleyiniz.".format(str(self.banner))

    def getTitle(self):
        if self.title == 1:
            return "Banner Yönetimi"

    class Meta:
        verbose_name = "Modül"
        verbose_name_plural = "Modüller"


class Languages(models.Model):
    title = models.CharField(max_length=100)
    code = models.CharField(max_length=10)

    def __str__(self):
        return str(self.title)

    class Meta:
        verbose_name = "Dil"
        verbose_name_plural = "Dil Yönetimi"


class AdminGorevler(models.Model):
    title = models.CharField(max_length=250)
    active = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
