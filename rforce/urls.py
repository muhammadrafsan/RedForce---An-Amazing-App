from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='loginpage'),
    path('home/', views.home, name='homepage'),
    path('upload/', views.upload, name='upload'),
    path('setUpProfile/', views.setUpProfile, name='setUpProfile'),
    path('faceRecog/', views.faceRecog, name='faceRecog'),
    path('check/', views.check, name='check'),
    #path('face_recog', views.faceRecog, name='face_recog'),
    path('logout/', views.logout, name='logout'),
    path('uploadfile/', views.uploadfile, name='uploadfile'),
    path('viewfile/', views.viewfile, name='viewfile'),
    path('openfile/<id>/', views.openfile, name='openfile'),
    path('deletefile/<id>/', views.deletefile, name='deletefile'),
]
