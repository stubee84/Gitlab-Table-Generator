from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
  # TEMPORARY
    path('generatetable', views.generate_table, name='generatetable'),
    # path('signout', views.home, name='signout'),
    # path('calendar', views.home, name='calendar'),
]