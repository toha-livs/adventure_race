from django.contrib import admin
from .models import ControlPoint, CPProtocol, RunGuys, ResultRuns


@admin.register(CPProtocol)
class CPProtocolAdmin(admin.ModelAdmin):
    list_filter = ['number', 'control_point__name']



admin.site.register(ControlPoint)
admin.site.register(RunGuys)
admin.site.register(ResultRuns)
