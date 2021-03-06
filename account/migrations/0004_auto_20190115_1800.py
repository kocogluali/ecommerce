# Generated by Django 2.0 on 2019-01-15 15:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_sepet_cargo'),
    ]

    operations = [
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('code', models.CharField(max_length=100)),
                ('last_date', models.DateTimeField()),
                ('qty', models.IntegerField(default=0)),
                ('active', models.BooleanField(default=True)),
                ('disc_price', models.DecimalField(decimal_places=2, default=0, max_digits=20)),
            ],
        ),
        migrations.AddField(
            model_name='sepet',
            name='totalWithCoupon',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=9),
        ),
        migrations.AddField(
            model_name='sepet',
            name='coupon',
            field=models.ForeignKey(blank=True, null=True, on_delete=None, to='account.Coupon'),
        ),
    ]
