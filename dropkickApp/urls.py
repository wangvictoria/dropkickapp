from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('download/', views.download_file, name='download'),
    path('download_sample/', views.download_sample, name='download_sample'),
    #path('upload/', views.upload_file, name='upload'),
    #path('process/', views.process, name='process'),
]