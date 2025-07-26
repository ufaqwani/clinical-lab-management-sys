from django.urls import path
from . import views

urlpatterns = [
    path('', views.report_list, name='report_list'),
    path('generate/', views.generate_report, name='generate_report'),
    path('batch-generate/', views.batch_generate_reports, name='batch_generate_reports'),
    path('<str:report_id>/', views.report_detail, name='report_detail'),
    path('<str:report_id>/download/', views.download_report, name='download_report'),
]
