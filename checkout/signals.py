# Make models and signals connected

"""
We need a way to update the order total, delivery cost, and grand_total for each order as users add line items to it.
   The basic process is that 
    1. first: create an order.
	2. second: iterate through the shopping bag.
	3. third: add line items to it one by one updating the various costs along the way.
We've got the method to update the total in the Order model.
	We need a way to call it each time a line item is attached to the order.
	  To accomplish this we'll use a BUILT-IN feature of django called SIGNALS.
signals.py has to live at the same level as models.py

To let django know that there's a new signals module with some listeners in it 
we just need to make a change to apps.py too.
"""

# import two signals post_save  and  post_delete  where post, in this case, means AFTER
# this implies these signals are sent by django to the entire application after a model instance is saved and after it's deleted respectively
from django.db.models.signals import post_save, post_delete

# To receive signals import receiver from django.dispatch
# (since we'll be listening for signals from the OrderLineItem model we'll also need that)
from django.dispatch import receiver

from .models import OrderLineItem

# to execute update_on_save() function anytime the post_save signal is sent,
# use the receiver decorator telling it we're receiving post saved signals from the OrderLineItem model
@receiver(post_save, sender=OrderLineItem)
# a special type of function which handle signals from the   post_save   event.
# it's parameters refer to:
#  the    sender    of the signal, in our case OrderLineItem 
#  the actual    instance    of the model that sent it
#  a boolean,   created   , sent by django referring to whether this is a new instance or one being updated
#  a **kwargs    any keyword arguments   
def update_on_save(sender, instance, created, **kwargs):
    """
    Update order total on lineitem update/create
    """
    # access instance.order (it refers to the order this specific line item is related to)
    # and call the update_total method on it
    instance.order.update_total()

# handle updating the totals when a line item is deleted
@receiver(post_delete, sender=OrderLineItem)
def update_on_save(sender, instance, **kwargs):
    """
    Update order total on lineitem delete
    """
    instance.order.update_total()