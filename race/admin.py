from django.contrib import admin
from .models import ControlPoint, CPProtocol, RunGuys, ResultRuns

admin.site.register(CPProtocol)
admin.site.register(ControlPoint)
admin.site.register(RunGuys)
admin.site.register(ResultRuns)
