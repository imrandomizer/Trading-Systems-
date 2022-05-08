from django.urls import path

from . import views

#BELONGS TO Analysis Ready Server.

urlpatterns = [
	path('DeleveriesAPI',views.DeleveriesAPI,name="DeleveriesAPI"),
    path('participantDataAPI',views.participantDataAPI,name="participantDataAPI"),
    path('',views.index,name='index'),
    path('getBarometerData',views.getBarometerData,name='getBarometerData'),
    path('Dates',views.availDates,name="availDates"),
    path('RefreshConstantFiles',views.refreshConstantFiles,name="refreshConstantFiles")
    ]


#print("ONE TIME SETUP CODE")