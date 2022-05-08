from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('DeliveryPatterns',views.DeliveryPatterns,name='DeliveryPatterns'),
    path('table_deliverable_low_high',views.table_deliverable_low_high,name="table_deliverable_low_high"),
    path('DerivativeDataAnalysis',views.DerivativeDataAnalysis,name="DerivativeDataAnalysis"),
    path('MarketActivity',views.MarketActivity,name="MarketActivity"),
    path('fetchSymbolDerivativeData',views.fetchSymbolDerivativeData,name="fetchSymbolDerivativeData"),
    path('Barometer',views.barometer,name="barometer"),
    path('BarometerData',views.getNewBarometerData,name="getNewBarometerData")
]