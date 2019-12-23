from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    path('', views.index),
    path('search/', views.search),
    path('kg/', views.kg),
    path('kg/show/', views.show),
    url(r'^kg_search/.*', views.kg_search)
]
