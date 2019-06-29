from django import template
from datetime import datetime

register = template.Library()


@register.simple_tag(name="d_v_date")
def d_v(dict_obj: dict, key_obj: str):
    if dict_obj.get(str(key_obj)):
        return datetime.strftime(datetime.fromtimestamp(dict_obj.get(str(key_obj))), '%d <u>%H:%M:%S</u>')
    return '-'
