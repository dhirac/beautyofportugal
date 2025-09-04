# yourapp/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def sum_prices(order_items):
    return sum(item.price * item.quantity for item in order_items)
