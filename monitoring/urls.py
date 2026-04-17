from django.urls import path
from . import views

urlpatterns = [
    path('', views.riwayat_laporan, name='riwayat_laporan'),
    path('simpan/', views.simpan_laporan, name='simpan_laporan'),
]
