from django.urls import path
from .views import HomeView, CPView, ExcelDump, DeleteCpp, ResultsGuest, ExcelUpload, test_cpp, review_result

urlpatterns = [
    path('', ResultsGuest.as_view(), name='guest'),
    path('home', HomeView.as_view(), name='home'),
    path('cpp', CPView.as_view(), name='cpp'),
    path('cpp-delete-all', DeleteCpp.as_view(), name='delete_cpp'),
    path('excel-dump', ExcelDump.as_view(), name='excel_dump'),
    path('excel-upload', ExcelUpload.as_view(), name='excel_upload'),
    path('test', test_cpp, name='test'),
    path('review-result', review_result, name='review-result')
]