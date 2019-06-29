from django.contrib import admin
from .models import ControlPoint, CPProtocol

admin.site.register(CPProtocol)
admin.site.register(ControlPoint)
