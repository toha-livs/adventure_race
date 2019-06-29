from django import template

register = template.Library()

@register.assignment_tag
def get_result_tag(arg1, arg2, arg3):
    "----"
    return "response"