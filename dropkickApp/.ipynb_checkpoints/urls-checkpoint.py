from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    #path('export/', download_csv, name='export')
    #path('upload/', views.upload_file, name='upload'),
    #path('process/', views.process, name='process'),
]