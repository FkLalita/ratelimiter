from django.urls import path
from . import views

urlpatterns = [
    path('ratelimit', views.tester, name='ratelimit'),
]
