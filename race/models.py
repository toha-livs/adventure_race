import json

from django.contrib.auth.models import User
from django.db.models import Model, CharField, ForeignKey, CASCADE, IntegerField, DateTimeField, TextField
from django.db import models


class ControlPoint(Model):
    name = CharField(max_length=64)
    user = models.ForeignKey(User, on_delete=CASCADE)
    order = IntegerField(unique=True)
    description = CharField(max_length=1024, blank=True)

    class Meta:
        db_table = 'control_point'
        ordering = ['order']
        verbose_name = 'Контрольный пункт'
        verbose_name_plural = 'Контрольные пункты'

    def __str__(self):
        return f'<ControlPoint: name={self.name}, manager={self.user}, order={self.order}, description={self.description}>'


class CPProtocol(Model):
    control_point = ForeignKey(ControlPoint, on_delete=CASCADE)
    number = IntegerField()
    date = DateTimeField()

    @property
    def cp_descr(self):
        return self.control_point.description


    class Meta:
        db_table = 'c_p_protocol'
        ordering = ['-date']
        verbose_name = 'Протокол Контрольного пункта'
        verbose_name_plural = 'Протоколы Контрольных пунктов'

    def __str__(self):
        return f'<ControlPoint: name={self.control_point.name}, manager={self.number}, order={self.date}>'


class ResultRuns(Model):
    pre_result = TextField()
    passed_checkpoint = TextField()
    date_update = DateTimeField()

    def get_dicts(self):
        return json.loads(self.pre_result), json.loads(self.passed_checkpoint)

    def __str__(self):
        return f'<ResultRuns: pre_result={self.pre_result}, passed_checkpoint={self.passed_checkpoint}'


class RunGuys(Model):
    number = IntegerField(unique=True)
    name = CharField(max_length=128)

    def __str__(self):
        return f'<RunGuys: number={self.number}, name={self.name}'
