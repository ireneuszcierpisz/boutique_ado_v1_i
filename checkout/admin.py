from django.contrib import admin
from .models import Order, OrderLineItem


# OrderLineItemAdminInline inherits from admin.TabularInline
class OrderLineItemAdminInline(admin.TabularInline):
    # This allows us to add and edit line items in the admin right from inside the Order model 
    model = OrderLineItem
    # make the lineitem_total in the form read only
    readonly_fields = ('lineitem_total',)


class OrderAdmin(admin.ModelAdmin):
    # add line items to the OrderAdmin interface
    # this allows us to add and edit line items in the admin right from inside the Order model 
    # so at an order we can see a list of editable line items on the same page rather 
    # than having to go to the order line item interface.
    inlines = (OrderLineItemAdminInline,)

    # add read-only fields that will be calculated by the model methods.
    # we don't want anyone to have the ability to edit them since it could compromise the integrity of an order
    readonly_fields = ('order_number', 'date',
                       'delivery_cost', 'order_total',
                       'grand_total',)

    # fields option allow us to specify the order of the fields in the admin interface
    # so the order stays the same as it appears in the model.
    fields = ('order_number', 'date', 'full_name',
              'email', 'phone_number', 'country',
              'postcode', 'town_or_city', 'street_address1',
              'street_address2', 'county', 'delivery_cost',
              'order_total', 'grand_total',)

    # use the list display option to restrict the columns that show up in the order list to only a few key items
    list_display = ('order_number', 'date', 'full_name',
                    'order_total', 'delivery_cost',
                    'grand_total',)

    # set items to be ordered by date in reverse chronological order putting the most recent orders at the top
    ordering = ('-date',)

# register the Order model and the OrderAdmin.
# not register the OrderLineItem model since it's accessible via the inlines on the Order model
admin.site.register(Order, OrderAdmin)