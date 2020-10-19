from django import template
from datetime import timedelta,datetime
import pytz

register = template.Library()

@register.simple_tag
def is_field_invalid(field,form_errors):
    if form_errors and field in form_errors:
        return "is-invalid"
    else:
        return ""

@register.simple_tag
def get_field_invalid_msg(field,form_errors,default):
    if form_errors and field in form_errors:
        return form_errors[field]
    else:
        return default

@register.simple_tag
def is_recent_account(creation_dt):
    d = datetime.now(pytz.UTC)-creation_dt
    if d.total_seconds() < (1440 * 60):
        return True
    else:
        return False


