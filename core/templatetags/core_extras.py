from django import template
from decimal import Decimal, InvalidOperation

register = template.Library()

@register.filter
def div(value, arg):
    """Divide the value by the argument"""
    try:
        # Convert to float first to handle string values
        value = float(value)
        arg = float(arg)
        if arg == 0:
            return 0
        return Decimal(str(value / arg))
    except (ValueError, ZeroDivisionError, InvalidOperation, TypeError):
        return 0

@register.filter
def mul(value, arg):
    """Multiply the value by the argument"""
    try:
        # Convert to float first to handle string values
        value = float(value)
        arg = float(arg)
        return Decimal(str(value * arg))
    except (ValueError, TypeError, InvalidOperation):
        return 0

@register.filter
def min_value(value, arg):
    """Return the minimum of two values"""
    try:
        # Convert to float first to handle string values
        value = float(value)
        arg = float(arg)
        return min(value, arg)
    except (ValueError, TypeError, InvalidOperation):
        return 0 