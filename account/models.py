from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils.crypto import get_random_string
from decimal import Decimal
from campaings.models import Campaign
from django.utils import timezone


class Sepet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    user_ip = models.GenericIPAddressField(null=True, blank=True)
    sepet_no = models.CharField(max_length=20, null=True, blank=True)
    sepet_tutar = models.DecimalField(max_digits=9, decimal_places=2)
    cargo = models.ForeignKey("Cargo", on_delete=None)
    coupon = models.ForeignKey('Coupon', on_delete=None, null=True, blank=True)

    def __str__(self):
        return self.sepet_no

    def save(self, *args, **kwargs):
        self.sepet_no = get_random_string(20, "0123456789abcdefghijk")
        super(Sepet, self).save(*args, **kwargs)

    def create_or_get_basket(self, user, user_ip):
        """
           sepet yoksa oluşturulur return edilir -- sepet varsa return edilir
        """
        basket = None
        try:
            try:
                cargo = Cargo.objects.first()
                if not cargo:
                    cargo = Cargo.objects.create(title="firstShouldBe", delivery_time="12saat", price=10)
            except:
                cargo = None
            if user and User.objects.filter(id=user.id):
                if not Sepet.has_basket(self, user, user_ip):
                    basket = Sepet.objects.create(user=user, user_ip=user_ip, sepet_tutar=0, cargo=cargo)
                else:
                    basket = Sepet.get_basket(Sepet, user, user_ip)
            else:
                if not Sepet.has_basket(self, None, user_ip):
                    basket = Sepet.objects.create(user_ip=user_ip, sepet_tutar=0, user=None, cargo=cargo)
                else:
                    basket = Sepet.get_basket(Sepet, None, user_ip)
        except Exception as e:
            print(e)
            print("hata burada olducreate or get basket")
        return basket

    def has_basket(self, user, user_ip):
        if user:
            basket = Sepet.objects.filter(user_ip=user_ip, user=user)
        else:
            basket = Sepet.objects.filter(user_ip=user_ip, user=None)
        if basket:
            return True
        return False

    def get_basket(self, user, user_ip):
        """
            Bu method yalnızca  [MODEL] Sepet.create_or_get_basket() içerisinden çağrılabilir aksi takdirde hata verebilir.
        """
        basket = None
        try:
            user = User.objects.get(id=user.id)
        except:
            user = None
        if user:
            if Sepet.objects.filter(user=user, user_ip=user_ip).exists():
                basket = Sepet.objects.get(user=user, user_ip=user_ip)
        else:
            if Sepet.objects.filter(user_ip=user_ip, user=None).exists():
                basket = Sepet.objects.get(user_ip=user_ip, user=None)
        return basket

    def update_basket(self, basket):
        """
            update_basket(bu) methodunu kullanmadan önce sepetUrunler tablosunu güncellediğinizden emin olun.
            using fields : SepetUrunler.totalPrice
        """
        totalBasketPrice = 0
        basket_items = SepetUrunler.get_basket_items(SepetUrunler, basket)
        for b in basket_items:
            totalBasketPrice += b.totalPrice
        basket.sepet_tutar = totalBasketPrice
        basket.save(update_fields=['sepet_tutar'])

    def basket_have_item(self, basket):
        if SepetUrunler.objects.filter(parent_sepet__id=basket.id).count() > 0:
            return True
        return False

    def get_basket_items(self, basket):
        if basket:
            return SepetUrunler.objects.filter(parent_sepet__id=basket.id)

    def remove_all_basket_items(self, basket):
        if basket:
            SepetUrunler.objects.filter(parent_sepet__id=basket.id).delete()
            basket.sepet_tutar = 0
            basket.save(update_fields=['sepet_tutar'])

    def move_old_basket_items_to_new_basket(self, oldBasket, newBasket):
        oldBasketItems = oldBasket.get_basket_items(oldBasket)
        for oldItem in oldBasketItems:
            oldItem.parent_sepet = newBasket
            oldItem.save(update_fields=["parent_sepet"])
        newBasket.update_basket(newBasket)
        newBasket.update_basket(oldBasket)

    def clone_old_basket_items_to_new_basket(self, oldBasket, newBasket):
        oldBasketItems = oldBasket.get_basket_items(oldBasket)
        for oldItem in oldBasketItems:
            if not oldItem.has_product(newBasket, oldItem.parent_product, SepetUrunler.get_detail_list_convert_integer_list(SepetUrunler, oldItem.details), oldItem.attr):
                newItem = oldItem
                newItem.pk = None
                newItem.parent_sepet = newBasket
                newItem.save()
        newBasket.update_basket(newBasket)
        newBasket.update_basket(oldBasket)


class SepetUrunler(models.Model):
    parent_sepet = models.ForeignKey('Sepet', on_delete=models.CASCADE)
    parent_product = models.ForeignKey('product.Product', on_delete=models.CASCADE)
    qty = models.SmallIntegerField()
    attr = models.CharField(max_length=150)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    totalPrice = models.DecimalField(max_digits=9, decimal_places=2)
    details = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return str(self.parent_sepet)

    def add_product(self, urun, qty, attrText, basket, selected_details):
        if basket:
            sepet_item = SepetUrunler.objects.create(parent_sepet=basket, parent_product=urun, qty=qty, attr=attrText, price=0, totalPrice=0)
            indirimTutari = Campaign.calcDiscountPrice(Campaign, sepet_item.parent_product)
            totalPrice = (Decimal(urun.price) - indirimTutari) * Decimal(qty)
            if selected_details:
                variant = self.parent_product.variant_set.get_product_variant(urun.id, selected_details)
                if variant:
                    price = (Decimal(urun.price) + Decimal(variant.price)) - indirimTutari
                    totalPrice = price * Decimal(qty)
                else:
                    price = Decimal(urun.price) - indirimTutari
                    totalPrice = price * Decimal(qty)
                sepet_item.details = str(selected_details)
            else:
                price = Decimal(urun.price) - indirimTutari
            basket.sepet_tutar += totalPrice
            basket.save(update_fields=['sepet_tutar'])
            sepet_item.price = price
            sepet_item.totalPrice = totalPrice
            sepet_item.save(update_fields=["price", "details", "totalPrice"])
            return True
        return False

    def has_product(self, basket, urun, selected_details, attrText):
        if selected_details:
            if SepetUrunler.objects.filter(parent_sepet=basket, parent_product=urun, attr=attrText).exists():
                return True
        elif SepetUrunler.objects.filter(parent_product=urun, parent_sepet=basket).exists():
            return True
        return False

    def get_detail_list_convert_integer_list(self, sepetItemDetails):
        details = str(sepetItemDetails).replace("[", "").replace("]", "").replace("None", "")
        detailList = []
        for d in details:
            if d != "," and d != "[" and d != " ":
                detailList.append(int(d))
        return detailList

    def get_basket_items(self, basket):
        items = SepetUrunler.objects.filter(parent_sepet=basket)
        return items

    def removeBasketItem(self, basketItemID):
        if self.objects.filter(id=basketItemID).exists():
            basketItem = self.objects.get(id=basketItemID)
            basket = Sepet.objects.get(id=basketItem.parent_sepet.id)
            basket.sepet_tutar -= basketItem.totalPrice
            basketItem.delete()
            basket.save(update_fields=['sepet_tutar'])
            return True
        return False


class TamSiparisler(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    user_ip = models.GenericIPAddressField(null=True, blank=True)
    user_sepet = models.ForeignKey(Sepet, on_delete=models.CASCADE)
    mail = models.CharField(max_length=50)
    adres_text = models.TextField()
    product_text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    cargo = models.ForeignKey('Cargo', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user_sepet)


class Adress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    city = models.ForeignKey('City', on_delete=models.CASCADE)
    province = models.ForeignKey('Province', on_delete=models.CASCADE, verbose_name="Şehir")
    postcode = models.IntegerField(verbose_name="Posta Kodu")
    adres = models.TextField()
    name = models.CharField(max_length=70, verbose_name="Adınız")
    last_name = models.CharField(max_length=70)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message="Telefon numarası şu şekilde girilmelidir: '+999999999'. 15 haneye kadar izin verilir.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    mail = models.EmailField(max_length=80)
    adres_name = models.CharField(max_length=50, verbose_name="Adres Adı", help_text="Adres Adı Örn : Evim")

    def __str__(self):
        return self.name


class City(models.Model):
    title = models.CharField(max_length=50)

    def __str__(self):
        return self.title


class Province(models.Model):
    title = models.CharField(max_length=50, verbose_name="İlçe")
    parent = models.ForeignKey('City', on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Cargo(models.Model):
    title = models.CharField(max_length=80)
    image = models.ImageField(upload_to="Cargo", null=True, blank=True)
    delivery_time = models.CharField(max_length=50)
    price = models.SmallIntegerField(null=True, blank=True)

    def __str__(self):
        return self.title


class Favorites(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    fav_p = models.ManyToManyField('product.Product')

    def __str__(self):
        return str(self.user)


class Coupon(models.Model):
    title = models.CharField(max_length=200)
    code = models.CharField(max_length=100)
    last_date = models.DateTimeField()
    qty = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    disc_price = models.DecimalField(decimal_places=2, max_digits=20, default=0)

    def __str__(self):
        return self.title

    def getCoupon(self, couponCode):
        try:
            coupon = Coupon.objects.get(code=couponCode, active=True, last_date__gte=timezone.now())
        except:
            coupon = None
        return coupon
