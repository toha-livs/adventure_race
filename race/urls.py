from django.urls import path
from .views import (HomeView, CPView, ExcelDump, NameUpload, DeleteCpp,
                    ResultsGuest, PasswordUpload, test_cpp, review_result, CPPView, delete_result)

urlpatterns = [
    path('', ResultsGuest.as_view(), name='guest'),
    path('home', HomeView.as_view(), name='home'),
    path('add-cpp-result', CPPView.as_view(), name='add_cpp_result'),
    path('cpp', CPView.as_view(), name='cpp'),
    path('cpp-delete-all', DeleteCpp.as_view(), name='delete_cpp'),
    path('excel-dump', ExcelDump.as_view(), name='excel_dump'),
    path('password-cp-upload', PasswordUpload.as_view(), name='password_cp_upload'),
    path('name-upload', NameUpload.as_view(), name='name_upload'),
    path('test', test_cpp, name='test'),
    path('review-result', review_result, name='review-result'),
    path('delete-result', delete_result, name='delete-result')
]