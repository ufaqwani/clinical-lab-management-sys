from django.urls import path
from . import views
from .views import create_test_type


urlpatterns = [
    path('', views.test_list, name='test_list'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('order/', views.test_order, name='test_order'),
    path('<str:test_id>/', views.test_detail, name='test_detail'),
    path('<str:test_id>/results/', views.test_enter_results, name='test_enter_results'),
    path('tests/create-test-type/', create_test_type, name='create_test_type'),


]
