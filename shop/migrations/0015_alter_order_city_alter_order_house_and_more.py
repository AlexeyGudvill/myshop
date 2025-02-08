# Generated by Django 4.1.7 on 2025-02-07 16:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0014_shopuser_apartment_shopuser_city_shopuser_house_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='city',
            field=models.CharField(max_length=100, verbose_name='Город'),
        ),
        migrations.AlterField(
            model_name='order',
            name='house',
            field=models.CharField(max_length=20, verbose_name='Дом'),
        ),
        migrations.AlterField(
            model_name='order',
            name='postal_code',
            field=models.CharField(max_length=20, verbose_name='Почтовый индекс'),
        ),
        migrations.AlterField(
            model_name='order',
            name='street',
            field=models.CharField(max_length=255, verbose_name='Улица'),
        ),
    ]
