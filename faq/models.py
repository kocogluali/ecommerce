from django.db import models
from django.utils.translation import gettext_lazy as _
from ayarlar.models import Languages


class SSS(models.Model):
    title = models.CharField(verbose_name=_("baslik"), max_length=200)
    desc = models.TextField(verbose_name=_("aciklama"), null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Soru'
        verbose_name_plural = 'Sorular'

    def __str__(self):
        return self.title
