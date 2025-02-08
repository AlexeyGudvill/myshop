from django.urls import path
from . import views


app_name = 'shop'

urlpatterns = [
    path('', views.category_list, name='category_list'),
    path('category/<str:category_slug>/', views.product_list, name='product_list_by_category'),
    path('product/<int:id>/<str:slug>/', views.product_detail, name='product_detail'),
    path('products/', views.product_list, name='product_list'),
    path('registration/', views.registration, name='registration'),
    path('login_register/', views.login_register, name='login_register'),
    path('login_view/', views.login_view, name='login_view'),
    path('logout_view/', views.logout_view, name='logout_view'),
    path('profil/', views.profil, name='profil'),
    path('cart/', views.cart, name='cart'),
    path('cart/action/', views.cart_action, name='cart_action'),
    path('add_to_cart_or_order/<int:product_id>/', views.add_to_cart_or_order, name='add_to_cart_or_order'),
    path('order/', views.order, name='order'),
    path('order/remove/<int:order_id>/', views.remove_order, name='remove_order'),
    path('order/<int:order_id>/payment/', views.order_payment, name='order_payment'),
    path("save_address/", views.save_address, name="save_address"),
]
