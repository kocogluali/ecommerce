from django.db import models
from blog.models import Post
from django.contrib.auth.models import User
from decimal import Decimal


class ProductsComments(models.Model):
    user = models.ForeignKey('auth.user', on_delete=models.CASCADE)
    product = models.ForeignKey('product.Product', on_delete=models.CASCADE)
    content = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)
    votes = models.IntegerField()

    def __str__(self):
        return str(self.user)

    def addComment(self, user, product, content, votes):
        try:
            newComment = ProductsComments.objects.create(user=user, product=product, content=content, votes=votes)
            ProductsComments.updateProductAverage(ProductsComments, ProductsComments.objects.get(id=newComment.id).product)
            return True
        except Exception as e:
            print(e)
            return False

    def updateProductAverage(self, product):
        toplam = 0
        productComments = ProductsComments.objects.filter(product=product, active=True).values("votes")
        for v in productComments:
            toplam += v["votes"]
        if toplam > 0:
            print("büyük sıfırdan")
            ort = Decimal(toplam) / Decimal(productComments.count())
            pro = self.product  # todo : kontrol et
            pro.voteAverage = Decimal(ort)
            pro.save(update_fields=['voteAverage'])

    def save(self, *args, **kwargs):
        if self.active and self.id:
            self.updateProductAverage(ProductsComments.objects.get(id=self.id).product)
        super(ProductsComments, self).save(*args, **kwargs)


class BlogComments(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    blog = models.ForeignKey('blog.Post', on_delete=models.CASCADE)
    content = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user)

    def addComment(self, user, blog, content):
        try:
            BlogComments.objects.create(user=user, blog=blog, content=content)
            return True
        except Exception as e:
            print(e)
            return False

    def get_active_comments(self):
        return self.objects.filter(active=True).order_by("-id")
