from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('download/', views.download_file, name='download')
    #path('upload/', views.upload_file, name='upload'),
    #path('process/', views.process, name='process'),
]