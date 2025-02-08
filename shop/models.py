from django.db import models
from django.urls import reverse
from django.core.validators import MinLengthValidator
from django.utils.timezone import now


class Category(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, db_index=True, unique=True)
    image = models.ImageField(upload_to='category/%Y/%m/%d', blank=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_list_by_category',
                        args=[self.slug])


class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, db_index=True)
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True)
    short_description = models.TextField(blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('name',)
        index_together = (('id', 'slug'),)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_detail',
                        args=[self.id, self.slug])
    

class ShopUser(models.Model):
    email = models.EmailField(unique=True, verbose_name="Email")
    first_name = models.CharField(max_length=255, verbose_name="Имя")
    surname = models.CharField(max_length=255, verbose_name="Фамилия")
    phone_number = models.CharField(max_length=20, verbose_name="Телефон")
    password = models.CharField(max_length=128, verbose_name="Пароль")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата регистрации")
    
    city = models.CharField(max_length=100, verbose_name="Город", default="Не указан")
    street = models.CharField(max_length=255, verbose_name="Улица", default="Не указана")
    house = models.CharField(max_length=20, verbose_name="Дом", default="Не указан")
    apartment = models.CharField(max_length=20, verbose_name="Квартира", blank=True, null=True)
    postal_code = models.CharField(max_length=20, verbose_name="Почтовый индекс", default="Не указан")
    
    def __str__(self):
        return self.email


class Cart(models.Model):
    user = models.OneToOneField(ShopUser, on_delete=models.CASCADE, related_name="cart")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Корзина {self.user.email}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    is_selected = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class Order(models.Model):
    user = models.ForeignKey(ShopUser, on_delete=models.CASCADE, related_name="orders")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=50, default="Ожидает обработки")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)  # Итоговая цена
    
    city = models.CharField(max_length=100, verbose_name="Город")
    street = models.CharField(max_length=255, verbose_name="Улица")
    house = models.CharField(max_length=20, verbose_name="Дом")
    apartment = models.CharField(max_length=20, verbose_name="Квартира", blank=True, null=True)
    postal_code = models.CharField(max_length=20, verbose_name="Почтовый индекс")

    def __str__(self):
        return f"Заказ {self.id} от {self.user.email}"

    def update_total_price(self):
        self.total_price = sum(item.product.price * item.quantity for item in self.items.all())
        self.save()

    def set_status_ordered(self):
        self.status = "Заказан"
        self.updated_at = now()
        for item in self.items.all(): # Уменьшаем количество товара и обновляем доступность
            item.product.stock -= item.quantity 
            if item.product.stock <= 0:
                item.product.stock = 0
                item.product.available = False 
            item.product.save()

        self.save()

    def set_status_received(self):
        self.status = "Получен"
        self.save() 

    def is_valid(self): #Проверяет, заполнен ли адрес доставки
        return all([self.city != "", self.street != "", self.house != "", self.postal_code != "", 
                    self.city != "Не указан", self.street != "Не указана", self.house != "Не указан", self.postal_code != "Не указан"])

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    