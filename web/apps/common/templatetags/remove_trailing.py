from django import template

from decimal import Decimal as D

register = template.Library()


@register.filter(name="remove_trailing")
def remove_trailing(value):
    if value:
        d = D(str(value))
        return d.quantize(D(1)) if d == d.to_integral() else d.normalize()
    else:
        return