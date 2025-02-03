from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    return value * arg

@register.filter
def total_order_price(items):
    return sum(item.quantity * item.product.price for item in items)

@register.filter
def sum_order(items):
    i = 0
    for item in items:
        i+=1
    return i

@register.filter
def sum_cart(items):
    i = 0
    for item in items:
        if item.quantity:
            i+=1*item.quantity
        else:
            i+=1
    return i