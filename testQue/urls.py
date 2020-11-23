# -*- coding: utf-8 -*-

from django.urls import path

from . import views

urlpatterns = [
    path('reserve', views.reserve),
    path('create', views.create),
    path('complete', views.complete),
    path('getUserPos', views.get_user_pos),
    path('userReserved', views.user_reserved),
    path('delay', views.delay),
    path('message', views.message),
]
