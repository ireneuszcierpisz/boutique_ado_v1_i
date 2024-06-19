# Python Universal Unique Identifier class will be used to generate the order number
import uuid

from django.db import models
from django.db.models import Sum
from django.conf import settings

from products.models import Product

# Here are the models we need to create and track orders for anyone who makes a purchase

"""
As it's possible for the same customer to purchase the same things twice on separate occasions
which would result in us finding the first order in the database when they place the second one 
and thus the second-order never being added.
We can combat this by adding two new fields to the Order model.
The first is a TextField original_bag that will contain the original shopping bag that created it.
And the second is a CharField stripe_pid that contain the stripe payment intent id which is guaranteed to be unique.
"""

# the Order model will handle all orders across the store and is related to the OrderLineItem model
class Order(models.Model):
    # automatically generate this order number as we want it to be unique and permanent so users can find their previous orders
    order_number = models.CharField(max_length=32, null=False, editable=False)
    full_name = models.CharField(max_length=50, null=False, blank=False)
    email = models.EmailField(max_length=254, null=False, blank=False)
    phone_number = models.CharField(max_length=20, null=False, blank=False)
    country = models.CharField(max_length=40, null=False, blank=False)
    postcode = models.CharField(max_length=20, null=True, blank=True)
    town_or_city = models.CharField(max_length=40, null=False, blank=False)
    street_address1 = models.CharField(max_length=80, null=False, blank=False)
    street_address2 = models.CharField(max_length=80, null=True, blank=True)
    county = models.CharField(max_length=80, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    delivery_cost = models.DecimalField(max_digits=6, decimal_places=2, null=False, default=0)
    order_total = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0)
    original_bag = models.TextField(null=False, blank=False, default='')
    stripe_pid = models.CharField(max_length=254, null=False, blank=False, default='')

    # the first underscore by convention indicates it's a private method which will only be used inside this class
    def _generate_order_number(self):
        """
        Generate a random, unique order number using UUID
        """
        # return a random string of 32 characters
        return uuid.uuid4().hex.upper()

    def update_total(self):
        """
        Update grand total each time a line item is added,
        accounting for delivery costs.
        """
        # the aggregate function uses the sum function across all the lineitem_total fields for all line items on this order.
        # add a new field to the query set called lineitem_total_sum which we can then get and set the order_total to that
        self.order_total = self.lineitems.aggregate(Sum('lineitem_total'))['lineitem_total__sum'] or 0
        """
        by adding or zero to the end of line above that aggregates all the line item totals will prevent an error, 
        if we manually delete all the lineitems from an order, by making sure that this sets the order_total to zero instead of None.
        Without this, the next line would cause an error because it would try to determine if None is less than or equal to the delivery threshold.
        """
        if self.order_total < settings.FREE_DELIVERY_THRESHOLD:
            self.delivery_cost = self.order_total * settings.STANDARD_DELIVERY_PERCENTAGE / 100
        else:
            self.delivery_cost = 0
        self.grand_total = self.order_total + self.delivery_cost
        # save the instance
        self.save()

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the order number
        if it hasn't been set already.
        """
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number


# The OrderLineItem is like an individual shopping bag item 
# relating to a specific order, the product itself, the size that was selected, the quantity and the total cost for that line item
class OrderLineItem(models.Model):
    # here's a foreign key to the Order with a related name of 'lineitems' so 
    # when accessing orders we can make calls such as order.lineitems.all and order.lineitems.filter
    order = models.ForeignKey(Order, null=False, blank=False, on_delete=models.CASCADE, related_name='lineitems')
    # as we have a foreign key to the Product for this line item so that we can access all the fields of the associated product
    product = models.ForeignKey(Product, null=False, blank=False, on_delete=models.CASCADE)
    # that field can be null and blank since there are some products with no sizes
    product_size = models.CharField(max_length=2, null=True, blank=True) # XS, S, M, L, XL
    quantity = models.IntegerField(null=False, blank=False, default=0)
    lineitem_total = models.DecimalField(max_digits=6, decimal_places=2, null=False, blank=False, editable=False)

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the lineitem total
        and update the order total.
        """
        self.lineitem_total = self.product.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f'SKU {self.product.sku} on order {self.order.order_number}'