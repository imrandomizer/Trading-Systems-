from django.urls import path
#url file for fetchPriceInfo
from . import views

urlpatterns = [
    path('', views.index, name='index'),
]
