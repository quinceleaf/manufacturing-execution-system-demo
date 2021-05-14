from django import template

register = template.Library()


@register.simple_tag
def get_verbose_choice(object, field_name):
    if object._meta.get_field(field_name).choices:
        get_display = getattr(object, f"get_{field_name}_display")
        return get_display()
    else:
        get_display = getattr(object, field_name)
        if get_display == ("" or None):
            return "Not entered"
        else:
            return get_display
