from django.urls import path
#url file for Deleveries
from . import views

urlpatterns = [
    path('', views.index, name='index'),
]
