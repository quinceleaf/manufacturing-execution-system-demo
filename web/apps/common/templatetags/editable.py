from django import template
from django.contrib.auth.models import Group

register = template.Library()

""" 
Filter to be used in BOM detail pages to restrict edit functionality in UI
Returns true if BOM is in an editable state, false if not
Editable states are DRAFT, AWAITING, and RETURNED
Immutable states are APPROVED and SUPERSEDED
"""

EDITABLE_STATES = ["DRAFT", "AWAITING", "RETURNED"]
IMMUTABLE_STATES = ["APPROVED", "SUPERSEDED"]


@register.filter(name="editable")
def editable(obj):
    return True if obj.state in EDITABLE_STATES else False