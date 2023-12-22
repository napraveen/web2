from django.urls import path 
from . import views

urlpatterns=[
    path('',views.index,name='index'),
    path('start_video/', views.start_video, name='start_video'),
    path('stop_video/', views.stop_video, name='stop_video'),
    path('video/', views.video, name='video'),
    path('monitor', views.monitor, name='monitor'),
]