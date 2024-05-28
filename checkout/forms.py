# Create an order form

from django import forms
from .models import Order

# Create an OrderForm class 
# give OrderForm class Meta class to tell django which model it'll be associated with 
# and which fields we want to render.
# ! we're not rendering any fields in the form which will be automatically calculated
# means all calculations will be done via the model methods
class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('full_name', 'email', 'phone_number',
                  'street_address1', 'street_address2',
                  'town_or_city', 'postcode', 'country',
                  'county',)

    def __init__(self, *args, **kwargs):
        """
        Add placeholders and classes, remove auto-generated
        labels and set autofocus on first field
        """
        # override the init method of the form allow us to customize it
        # call the default init method to set the form up as it would be by default
        # use the super() method to call the constructor of the parent class and pass in the same arguments
        super().__init__(*args, **kwargs)
        # create a dictionary of placeholders which will show up in the form fields
        placeholders = {
            'full_name': 'Full Name',
            'email': 'Email Address',
            'phone_number': 'Phone Number',
            'country': 'Country',
            'postcode': 'Postal Code',
            'town_or_city': 'Town or City',
            'street_address1': 'Street Address 1',
            'street_address2': 'Street Address 2',
            'county': 'County',
        }

        # setting the autofocus attribute on the full name field to True
        # so the cursor will start in the full_name field when the user loads the page
        self.fields['full_name'].widget.attrs['autofocus'] = True
        # iterate through the forms fields 
        for field in self.fields:
            if self.fields[field].required:
                # adding a star * to the placeholder if it's a required field on the model.
                placeholder = f'{placeholders[field]} *'
            else:
                placeholder = placeholders[field]
            # Sett all the placeholder attributes to their values in the dictionary above
            self.fields[field].widget.attrs['placeholder'] = placeholder
            # Add a CSS class we'll use later.
            self.fields[field].widget.attrs['class'] = 'stripe-style-input'
            # remove the form fields labels since we won't need them given the placeholders are now set
            self.fields[field].label = False