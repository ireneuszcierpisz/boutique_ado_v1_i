from django.urls import path
from . import views

# as the webhook function live in webhooks.py file 
# import the webhook function from .webhooks
from .webhooks import webhook

urlpatterns = [
    path('', views.checkout, name='checkout'),
    path('checkout_success/<order_number>', views.checkout_success, name='checkout_success'),
    # to get webhook handler listening we need create a url for it
    # call this path 'wh/' and it will return a function called webhook with the name of webhook
    path('wh/', webhook, name='webhook'),
]
