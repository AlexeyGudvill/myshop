from django.shortcuts import render, get_object_or_404, redirect, get_list_or_404
from .models import ShopUser, Cart, CartItem, Order, OrderItem, Category, Product
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from django.http import JsonResponse
from django.core.mail import send_mail


def category_list(request, category_slug=None): # страница категорий
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    return render(request,
                  'shop/product/index.html', {'products': products, 'category': category, 'categories': categories})

def product_list(request, category_slug=None): # товары по категориям + поиск + сортировка по параметру
    category = None
    categories = Category.objects.all()
    query = request.GET.get('query', '').strip()
    sort = request.GET.get('sort')
    products = Product.objects.filter(available=True)

    if category_slug: # Фильтрация по категории
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    if query: # Фильтрация по поиску
        products = products.filter(name__icontains=query.capitalize())

    # Применение сортировки
    if sort == 'name':
        products = products.order_by('name')
    elif sort == 'price':
        products = products.order_by('price')
    elif sort == 'stock':
        products = products.order_by('-stock')
    return render(request, 'shop/product/list.html', {'products': products, 'category': category, 'categories': categories, 'query': query, 'sort': sort})


def product_detail(request, id, slug): # описание товара
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    return render(request,
                  'shop/product/detail.html',
                  {'product': product})


def registration(request): # страница регистрации
    return render(request, 'shop/registration.html')

              
def login_register(request): # регистрация
    if request.method == 'POST':
        email = request.POST['email']
        full_name = request.POST['full_name']
        phone_number = request.POST['phone_number']
        password = request.POST['password']

        if ShopUser.objects.filter(email=email).exists():
            messages.error(request, "Пользователь с таким логином уже существует.")
            return redirect('shop:registration')
        
        user = ShopUser.objects.create(
            email=email,
            full_name=full_name,
            phone_number=phone_number,
            password=make_password(password)
        )
        Cart.objects.create(user=user)  # Создаём корзину для пользователя
        messages.success(request, "Регистрация успешна. Выполните вход.")

    return render(request, 'shop/registration.html')


def login_view(request): # вход
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        try:
            user = ShopUser.objects.get(email=email)
        except ShopUser.DoesNotExist:
            messages.error(request, "Неверный логин или пароль.")
            return redirect('shop:registration')

        if check_password(password, user.password):
            request.session['user_id'] = user.id
            request.session['email'] = user.email
            messages.success(request, f"Добро пожаловать, {user.full_name}!")
            return redirect('shop:profil')
        else:
            messages.error(request, "Неверный логин или пароль.")
            return redirect('shop:registration')

    return render(request, 'shop/registration.html')


def logout_view(request): # выход из аккаунта
    request.session.flush()  # Удаляем сессию
    messages.success(request, "Вы вышли из системы.")
    return redirect('shop:registration')


def profil(request): # страница профиля
    if 'user_id' not in request.session:
        return redirect('shop:registration')

    user = ShopUser.objects.get(id=request.session['user_id'])
    cart = user.cart  # Корзина пользователя
    orders = user.orders.all()
    pending_orders = orders.filter(status="Ожидает обработки")
    ordered_orders = orders.filter(status="Заказан")
    return render(request, 'shop/profil.html', {'user': user, 'pending_orders': pending_orders, 'ordered_orders': ordered_orders, 'cart': cart})


def cart(request): # страница корзины
    if 'user_id' not in request.session:
        return redirect('shop:registration')
    
    user = ShopUser.objects.get(id=request.session['user_id'])
    cart = user.cart  # Корзина пользователя
    return render(request, 'shop/cart.html', {'user': user, 'cart': cart})


def order(request): # страница заказов
    if 'user_id' not in request.session:
        return redirect('shop:registration')

    user = ShopUser.objects.get(id=request.session['user_id'])
    orders = user.orders.all()  # Все заказы пользователя
    pending_orders = orders.filter(status="Ожидает обработки")
    ordered_orders = orders.filter(status="Заказан")
    return render(request, 'shop/order.html', {'user': user, 'orders': orders, 'pending_orders': pending_orders, 'ordered_orders': ordered_orders})


def add_to_cart_or_order(request, product_id): # действия с товарами: добавить в корзину или заказать
    if 'user_id' not in request.session:
        return redirect('shop:registration')

    user = ShopUser.objects.get(id=request.session['user_id'])
    product = get_object_or_404(Product, id=product_id)
    action = request.POST.get('action', 'cart')  # Проверяем, что за действие: добавить в корзину или заказать

    if action == 'order': # Логика оформления заказа напрямую
        order = Order.objects.create(user=user)
        OrderItem.objects.create(order=order, product=product, quantity=1)
        return redirect('shop:order')
    
    elif action == 'cart': # Логика добавления в корзину
        cart = user.cart
        item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        item.quantity += 1
        item.save()
        return redirect('shop:cart')

    return redirect('shop:cart')


def cart_action(request): # действия с товарами в корзине: удалить или заказать
    if 'user_id' not in request.session:
        return redirect('shop:registration')

    if request.method == "POST":
        action = request.POST.get('action')
        selected_items = request.POST.getlist('selected_items')
        user = ShopUser.objects.get(id=request.session['user_id'])
        cart = user.cart

        if action == "order":  # Логика оформления заказа
            if selected_items:
                order = Order.objects.create(user=user)
                for item_id in selected_items:
                    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
                    OrderItem.objects.create(order=order, product=cart_item.product, quantity=cart_item.quantity)
                CartItem.objects.filter(id__in=selected_items).delete() # Удаляем оформленные товары из корзины
            return redirect('shop:order')
        
        elif action == "remove": # Логика удаления товаров
            for item_id in selected_items:
                cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
                if cart_item.quantity > 1:
                    cart_item.quantity -= 1
                    cart_item.save()
                else:
                    cart_item.delete()
            return redirect('shop:cart')

    return redirect('shop:cart')


def remove_order(request, order_id): # удаление заказа
    if 'user_id' not in request.session:
        return redirect('shop:registration')

    user = ShopUser.objects.get(id=request.session['user_id'])
    order = get_object_or_404(Order, id=order_id, user=user)

    if order.status == "Ожидает обработки":
        order.delete()
    
    return redirect('shop:order') 


def order_payment(request, order_id): # заказ товара - оплата
    if 'user_id' not in request.session:
        return redirect('shop:registration')

    order = get_object_or_404(Order, id=order_id, user__id=request.session['user_id'])
    order.update_total_price()

    if request.method == "POST":
        # Симуляция оплаты (можно интегрировать платежный шлюз)
        order.set_status_ordered()

        # Отправка письма
        send_mail(
            'Ваш заказ оформлен',
            f'Ваш заказ №{order.id} успешно оформлен на сумму {order.total_price} руб.',
            'agoodwill04@gmail.com',
            ['agoodwill04@gmail.com'],
            fail_silently=False,
        )

        return redirect('shop:order')  # Перенаправление на страницу заказов

    return render(request, 'shop/order_payment.html', {'order': order})