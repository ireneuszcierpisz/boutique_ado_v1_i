"""
Write a custom template filter to calculate the subtotal value in the bag;
For the subtotal column, the subtotal should be the quantity times the product price
"""

# as there is the empty file called __init__.py in templatetags folder
# so that templatetags directory is treated as a Python package
# making bag_tools.py module available for imports and to use in templates
from django import template

# create a variable register which is an instance of template library
register = template.Library()

# use the register filter decorator to register  function calc_subtotal as a template filter
# (django doc: creating custom template tags and filters)
@register.filter(name='calc_subtotal')

# define the filter which returns a product of price and quantity
def calc_subtotal(price, quantity):
    return price * quantity