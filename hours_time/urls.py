from django.urls import path
from hours_time import views


urlpatterns = [
    path('report/', views.reports, name='report'),
]
