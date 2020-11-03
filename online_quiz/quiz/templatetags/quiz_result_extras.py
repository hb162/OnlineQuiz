from django import template

register = template.Library()


@register.filter()
def to_int(value):
    return int(value)


@register.filter
def as_percentage_of(part, whole):
    try:
        return "%d%%" % (float(part) / whole * 100)
    except (ValueError, ZeroDivisionError):
        return ""


@register.filter
def to_set(value):
    return set(value)