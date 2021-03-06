# Generated by Django 3.1.7 on 2021-03-12 17:59

from decimal import Decimal
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('products', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BaseBasket',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('price', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=10, verbose_name='Price')),
                ('session_id', models.CharField(blank=True, max_length=255, null=True, verbose_name='Session id')),
                ('basket_items', models.ManyToManyField(blank=True, related_name='basket', to='products.BasketItem', verbose_name='Basket item')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'Basket',
                'verbose_name_plural': 'Baskets',
            },
        ),
    ]
