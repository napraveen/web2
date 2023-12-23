from django.urls import path 
from . import views

urlpatterns=[
    path('',views.index,name='index'),
    path('start_video/', views.start_video, name='start_video'),
    path('stop_video/', views.stop_video, name='stop_video'),
    path('video/', views.video, name='video'),
    path('monitor', views.monitor, name='monitor'),
    path('crack_detection', views.crack_detection, name='crack_detection'),
    path('showimages/', views.showimages, name='showimages'),
    path('showcorrodedimages/', views.showcorrodedimages, name='showcorrodedimages'),
    path('selectoption/', views.selectoption, name='selectoption'),
    path('corrosion_detection', views.corrosion_detection, name='corrosion_detection'),
]