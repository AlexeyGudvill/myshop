# Generated by Django 4.1.7 on 2025-01-17 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0005_alter_cartitem_quantity'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='is_selected',
            field=models.BooleanField(default=False),
        ),
    ]
