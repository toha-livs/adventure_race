import json

import pandas as pd
import xlsxwriter as xlsxwriter
import datetime
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.utils import timezone
from django.views.generic.base import View
from io import BytesIO
from race.models import ControlPoint, CPProtocol, ResultRuns, RunGuys


class AdminView(View):

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        return HttpResponseForbidden()


class Scope:
    final = []
    usage_list = []
    cp_usage = []

    def __init__(self, runers: list, cp: list):
        self.runers = runers
        self.cp = cp

    def get_true_runers(self, cp, cleared=True):
        response = []
        old_runers = list(self.usage_list)
        for runer in old_runers:
            if runer.get(cp['id']):
                response.append(runer)
                if cleared:
                    self.usage_list.pop(self.usage_list.index(runer))
        return response

    def find_key(self, x, cp):
        return x[cp['id']]

    def run(self):
        self.cp_usage = list(self.cp)
        self.cp_usage.reverse()
        self.usage_list = self.runers
        for cp in self.cp_usage:
            runers = self.get_true_runers(cp, cleared=True)
            runers.sort(key=lambda x: x[cp['id']])
            self.final += runers


class Results:
    passed_checkpoints = []
    response = []
    pre_response = {}

    def __init__(self):
        cpp = self.get_cp()
        self.run_cp(cpp)
        self.format_list(sort=False)
        self.set_run_names()
        self.save_result()

    def save_result(self):
        res = ResultRuns.objects.all().first()
        print(self.response)
        if res:
            res.delete()
            ResultRuns(pre_result=json.dumps(self.response), passed_checkpoint=json.dumps(self.passed_checkpoints),
                       date_update=timezone.now()).save()
        else:
            ResultRuns(pre_result=json.dumps(self.response), passed_checkpoint=json.dumps(self.passed_checkpoints),
                       date_update=timezone.now()).save()

    @staticmethod
    def get_cp():
        return CPProtocol.objects.filter(date__isnull=False, number__isnull=False).order_by('control_point__order')

    def set_run_names(self):
        upd_resp = []
        for run in self.response:
            guy = RunGuys.objects.filter(number=run['number']).first()
            if guy:
                run.update({'name': guy.name})
            upd_resp.append(run)
        self.response = upd_resp

    def format_list(self, sort=False):
        for key, value in self.pre_response.items():
            self.response.append({'number': key, **value})
        if sort:
            list_sorted = Scope(self.response, self.passed_checkpoints)
            list_sorted.run()
            self.response = list_sorted.final

    def run_cp(self, cpp):
        cpp.order_by('number')
        for cp in cpp:
            if self.pre_response.get(cp.number):
                self.pre_response[cp.number].update({cp.control_point.id: cp.date.timestamp()})
            else:
                self.pre_response[cp.number] = {'number': cp.number, cp.control_point.id: cp.date.timestamp()}
            if {'id': cp.control_point.id, 'name': cp.control_point.name} not in self.passed_checkpoints:
                self.passed_checkpoints.append({'id': cp.control_point.id, 'name': cp.control_point.name})
        # print(self.response)


class WriterMessages:

    @staticmethod
    def write_msg(request, success: bool, title: str, content=None):
        messages.add_message(request, messages.INFO, json.dumps({'msg_title': title,
                                                                 'success': ('bad', True)[success],
                                                                 'msg_content': content}))
        return request

    @staticmethod
    def check_message(storage: list) -> dict:
        message = [str(i) for i in storage]
        if not message:
            return {}
        message = message[0]
        date_update = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
        context = {'status':
                       {'msg_title': json.loads(message).get('msg_title', None),
                        'msg_content': json.loads(message).get('msg_content', None),
                        'msg_footer': f'Дата обновления {date_update}',
                        'success': json.loads(message)['success']
                        }}
        return context


class XLSXClass:
    ws = None
    headers = []
    colums = None
    date_time_wb_format = None

    def __init__(self, file, cont_point=False, name=False):
        self.file = file
        self.cont_point = cont_point
        self.name = name

    @staticmethod
    def format_date(date):
        print(f'####date##{date}####')
        date = date.strip()
        if 'NaT' in date or 'NaN' in date:
            return None
        if '-' in date:
            if '.' in date:
                response = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f')
            else:
                response = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        elif '/' in date:
            if '.' in date:
                response = datetime.datetime.strptime(date, '%Y/%m/%d %H:%M:%S.%f')
            else:
                response = datetime.datetime.strptime(date, '%d/%m/%Y %H:%M:%S')
        else:
            raise ValueError
        return response

    @staticmethod
    def int_formater(word: str):
        print(f'####int####{word}####')
        try:
            return int(word)
        except:
            return None

    @staticmethod
    def testing(word):
        return word

    @staticmethod
    def pars_pass(word: str) -> str:
        word = word.strip()
        if 'NaN' in word or len(word) < 4:
            raise SyntaxError
        return word.strip()

    def start_pars(self):
        test = pd.read_excel(self.file, index_col=0)
        print(test)
        if self.cont_point:
            return [{'number': int(row[:row.find(' ')]), 'password': self.pars_pass(row[row.rfind('  '):])} for row in
                    str(test).split('\n')[2:]]
        if self.name:
            return [{'number': int(row[:row.find(' ')]), 'name': row[row.rfind('  '):].strip()} for row in
                    str(test).split('\n')[2:]]
        response = []
        for dct in [{'number': self.int_formater(row[:row.find(' ')]), 'date': self.format_date(row[row.rfind('  '):])}
                    for row in
                    str(test).split('\n')[2:]]:
            if dct['number'] is not None and dct['date'] is not None:
                response.append(dct)
        return response

    def _write_header(self, colums):
        self.ws.write(0, 0, 'Number')
        for id, item in enumerate(colums):
            self.ws.write(0, id + 1, item['name'])

    @staticmethod
    def check_is_valid(date):
        if isinstance(date, float):
            print(date, datetime.datetime.fromtimestamp(date))
            return datetime.datetime.fromtimestamp(date)
            # date = datetime.datetime.fromtimestamp(date)
            # return datetime.datetime.strftime(date, '%d %H:%M:%S')
        elif isinstance(date, int):
            return date
        return None

    def _write_data(self, pre_result):
        for row, i in enumerate(pre_result):
            print(i.get('number'), '####i')
            row = row + 1
            self.ws.write(row, 0, self.check_is_valid(i.get('number')))
            for num_col, col in enumerate(self.colums):
                num_col = num_col + 1
                self.ws.write(row, num_col, self.check_is_valid(i.get(str(col['id']))), self.date_time_wb_format)

    def start_write(self, colums, pre_result):
        self.colums = colums
        file = BytesIO()
        wb = xlsxwriter.Workbook(file)
        self.date_time_wb_format = wb.add_format({'num_format': 'dd-mm-yyyy hh:mm:ss'})
        self.ws = wb.add_worksheet()
        self._write_header(colums)
        self._write_data(pre_result)
        wb.close()
        xlsx_data = file.getvalue()
        return xlsx_data


def post_from_stuff(request) -> dict:
    control_point = ControlPoint.objects.filter(user=request.user).first()
    CPProtocol.objects.filter(control_point=control_point).delete()
    context = dict(c_p=control_point)
    pars_file = XLSXClass(request.FILES['file'])
    date_update = datetime.datetime.strftime(timezone.now(), '%Y-%m-%d %H:%M:%S')
    try:
        data_dict = pars_file.start_pars()
    except ValueError as ex:
        context['status'] = {'msg_title': 'Файл не загружен',
                             'msg_content': f'''Проверите валидность данных: номер "234", дата "2018-05-24 12:43:00"
                            проверьте строку <{ex}> 
                         ''',
                             'msg_footer': f'Дата обновления {date_update}',
                             'success': 'bad'
                             }
        return context
    CPProtocol.objects.bulk_create(
        [CPProtocol(control_point=control_point, number=cpp['number'], date=cpp['date']) for cpp in data_dict])
    context['status'] = {'msg_title': 'Файл загружен успешно',
                         'msg_content': f'Данные обновлены, на кп "{control_point.name}", записано участников ({len(data_dict)}), спасибо за сотрудничество',
                         'msg_footer': f'Дата обновления {date_update}',
                         'success': True
                         }
    return context
