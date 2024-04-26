from django.urls import path
from . import views

urlpatterns = [
    # one empty path to indicate that this is the route URL.
    # It renders views.index with the name of home.
    path('', views.index, name='home'),
]