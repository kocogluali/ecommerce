# Generated by Django 2.1.5 on 2019-01-30 13:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ayarlar', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitesettings',
            name='phone',
            field=models.CharField(default=1, max_length=20, verbose_name='Telefon Numarası'),
            preserve_default=False,
        ),
    ]
