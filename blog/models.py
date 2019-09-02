from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from ckeditor.fields import RichTextField
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver
import re
from comment import models as comModel


class PostCategory(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, editable=False, max_length=120)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    def get_url(self):
        return reverse("blog:blogList", kwargs={'category': self.slug})

    def get_unique_slug(self):
        slug = slugify(self.title.replace('ı', 'i'))
        unique_slug = slug
        counter = 1
        while Post.objects.filter(slug=unique_slug).exists():
            unique_slug = '{}-{}'.format(slug, counter)
            counter += 1
        return unique_slug

    def save(self, *args, **kwargs):
        self.slug = self.get_unique_slug()
        return super(PostCategory, self).save(*args, **kwargs)


class Post(models.Model):
    category = models.ForeignKey('blog.PostCategory', on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name='Yazar', on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=120, verbose_name='Başlık')
    content = RichTextField(verbose_name='İçerik')
    publishing_date = models.DateTimeField(verbose_name='Yayınlanma Tarihi', auto_now_add=True)
    image = models.ImageField(blank=True, null=True)
    slug = models.SlugField(unique=True, editable=False, max_length=130)
    active = models.BooleanField(default=True)
    tags = models.CharField(max_length=200, help_text="Lütfen kelimelerin arasında virgül kullanınız ve boşluk kullanmayınız", null=True, blank=True)

    def __str__(self):
        return self.title

    def tags_split(self):
        if self.tags:
            tagList = self.tags.split(",")
            newTagList = []
            for t in tagList:
                if t:
                    newTagList.append(t)
            return newTagList
        return None

    def get_comment_count(self):
        return comModel.BlogComments.objects.filter(active=True, blog__id=self.id).count()

    def get_url(self):
        return reverse("blog:blogDetail", kwargs={'category': self.category.slug, 'post': self.slug})

    def get_unique_slug(self):
        slug = slugify(self.title.replace('ı', 'i'))
        unique_slug = slug
        counter = 1
        while Post.objects.filter(slug=unique_slug).exclude(id=self.id).exists():
            unique_slug = '{}-{}'.format(slug, counter)
            counter += 1
        return unique_slug

    def save(self, *args, **kwargs):
        self.slug = self.get_unique_slug()
        return super(Post, self).save(*args, **kwargs)


@receiver(pre_save, sender=Post)
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
