from django.urls import path
from . import views

urlpatterns = [
    # one empty path to indicate that this is the route URL.
    # It renders views.index with the name of home.
    path('', views.view_bag, name='view_bag'),
    # the url for add_to_bag view, containing the item_id
    path('add/<item_id>/', views.add_to_bag, name='add_to_bag'),
    # add a URL for adjust_bag view
    path('adjust/<item_id>/', views.adjust_bag, name='adjust_bag'),
    # add a URL for remove_from_bag view
    path('remove/<item_id>/', views.remove_from_bag, name='remove_from_bag'),
]