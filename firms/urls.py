from django.urls import path
from . import views

urlpatterns = [
    path('', views.firm_list, name='firm_list'),
    path('<int:firm_id>/', views.firm_detail, name='firm_detail'),
    path('profilim/', views.firm_profile, name='firm_profile'),
]