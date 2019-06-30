from wsgiref.util import FileWrapper

import pandas as pd

from django.db.utils import IntegrityError
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.views.generic.base import View
from django.contrib import messages
from race.models import ControlPoint, CPProtocol, ResultRuns, RunGuys
from race.utils import post_from_stuff, WriterMessages, Results, AdminView, XLSXClass


class HomeView(View, WriterMessages):
    http_method_names = ['get', 'post']

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, **kwargs):
        if request.user.is_superuser:
            cpp = ResultRuns.objects.all().first()
            context = dict()
            if cpp:
                runers, colums = cpp.get_dicts()
                context = {'runer': runers,
                           'colums': colums
                           }
            context.update({'c_p': {'name': 'Admin'}})
            context.update(self.check_message(messages.get_messages(request)))
            return render(request, 'race/super_home.html', context=context)
        control_point = ControlPoint.objects.filter(user=request.user).first()
        return render(request, 'race/home.html', context={'status': False, 'c_p': control_point})

    def post(self, request, **kwargs):
        context = post_from_stuff(request)
        print('hi')
        Results()
        print('hi')
        return render(request, 'race/home.html', context=context)


class ResultsGuest(View):

    def get(self, request, **kwargs):
        cpp = ResultRuns.objects.all().first()
        context = dict()
        if cpp:
            runers, colums = cpp.get_dicts()
            context = {'runer': runers,
                       'colums': colums
                       }
        return render(request, 'race/guest.html', context)


class CPView(AdminView, WriterMessages):

    def post(self, request, **kwargs):
        data = request.POST.dict()
        if len(data['password']) < 4:
            self.write_msg(request, False, 'Пароль должен состоять из 4 и больше символов')
            return redirect('home')
        try:
            with transaction.atomic():
                user = User.objects.create_user(data['login'], None, data['password'])
                user.save()
                ControlPoint(name=data['login'], order=data['order'], user=user).save()
                print('good')
        except Exception as ex:
            if str(ex)[str(ex).rfind(' ') + 1:] == 'auth_user.username':
                error = 'Имя КП не уникально'
            else:
                error = 'Номер КП не уникален'
            self.write_msg(request, False, error)
        return redirect('home')


class ExcelDump(AdminView, Results, XLSXClass):

    def get(self, request):
        result = ResultRuns.objects.all().first()
        pre_result, passed_checkpoints = result.get_dicts()
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename = your_template_name.xlsx'
        xlsx_data = self.start_write(passed_checkpoints, pre_result)
        response.write(xlsx_data)
        return response


class NameUpload(AdminView, WriterMessages):

    def post(self, request, **kwargs):
        try:
            data = XLSXClass(request.FILES['file'], name=True)
            data = data.start_pars()
        except SyntaxError:
            self.write_msg(request, False, 'Ошибка, данны в excel невалидны')
            return redirect('home')
        run_guys_obj = [RunGuys(**run_guy) for run_guy in data]
        try:
            RunGuys.objects.bulk_create(run_guys_obj)
            self.write_msg(request, True, f'Добавлено имен бегунов {len(run_guys_obj)}.')
            return redirect('home')
        except IntegrityError:
            self.write_msg(request, False, 'Ошибка, номера бегунов неуникальны')
            return redirect('home')


class PasswordUpload(AdminView, WriterMessages):

    def set_control_point(self, data, cp_sum=False):
        save_list = []
        try:
            with transaction.atomic():
                for cp in data:
                    name = 'CP{}'.format(cp['number'])
                    user = User.objects.create_user(name, None, cp['password'])
                    user.save()
                    save_list.append(ControlPoint(name=name, order=cp['number'], user=user))
                ControlPoint.objects.bulk_create(save_list)
        except IntegrityError:
            raise IntegrityError
        if cp_sum:
            return len(save_list)

    def post(self, request, **kwargs):
        try:
            data = XLSXClass(request.FILES['file'], cont_point=True)
            data = data.start_pars()
        except SyntaxError:
            self.write_msg(request, False, 'Ошибка, данны в excel невалидны')
            return redirect('home')
        try:
            cp_sum = self.set_control_point(data, cp_sum=True)
        except IntegrityError:
            self.write_msg(request, False, 'Ошибка в уникальности КП')
            return redirect('home')
        self.write_msg(request, True, f'Данные загружены успешно, добавлено {cp_sum} записи')
        return redirect('home')


class DeleteCpp(AdminView, WriterMessages):
    http_method_names = ['get']

    def get(self, request, **kwargs):
        User.objects.all().exclude(id=request.user.id).delete()
        ResultRuns.objects.all().delete()
        self.write_msg(request, True, 'Все КП удалены успешно')
        return redirect('home')


@login_required
@require_http_methods(["GET"])
def test_cpp(request):
    if request.user.is_superuser:
        Results()
        # cp = ControlPoint.objects.filter(id=id).first()
        # User.objects.filter(id=cp.user.id).first().delete()
        return redirect('home')


@login_required
@require_http_methods(["GET"])
def review_result(request):
    if request.user.is_superuser:
        Results()
        return redirect('home')