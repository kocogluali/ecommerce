# Generated by Django 2.1.5 on 2019-09-02 00:10

import django.core.files.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ayarlar', '0004_sitesettings_mail'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sitesettings',
            name='jsonFile',
            field=models.FileField(blank=True, null=True, storage=django.core.files.storage.FileSystemStorage(base_url='/home/murat/PycharmProjects/ecommerce', location='/home/murat/PycharmProjects/ecommerce'), upload_to='newsadmin/analitik/'),
        ),
    ]
