from django.urls import path
from . import views

urlpatterns = [
    # the 'products' url returns all_products view
    path('', views.all_products, name='products'),
    # the url contain the product ID, returns the product_detail view and is named 'product_detail':
    path('<product_id>', views.product_detail, name='product_detail'),
]
