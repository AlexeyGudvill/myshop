# Generated by Django 4.1.7 on 2025-01-16 14:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0003_cart_order_orderitem_cartitem'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShopUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=150, unique=True, verbose_name='Логин')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='Email')),
                ('full_name', models.CharField(max_length=255, verbose_name='ФИО')),
                ('phone_number', models.CharField(max_length=20, verbose_name='Телефон')),
                ('password', models.CharField(max_length=128, verbose_name='Пароль')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')),
            ],
        ),
        migrations.RenameField(
            model_name='cart',
            old_name='created',
            new_name='created_at',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='created',
            new_name='created_at',
        ),
        migrations.RemoveField(
            model_name='order',
            name='paid',
        ),
        migrations.RemoveField(
            model_name='order',
            name='updated',
        ),
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(default='Ожидает обработки', max_length=50),
        ),
        migrations.AlterField(
            model_name='cartitem',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.product'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.product'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='quantity',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='cart',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='cart', to='shop.shopuser'),
        ),
        migrations.AlterField(
            model_name='order',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='shop.shopuser'),
        ),
    ]
