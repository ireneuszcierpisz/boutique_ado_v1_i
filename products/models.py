from django.db import models

# create category model which will give our products a category like clothing, kitchen and dining, or deals
class Category(models.Model):

    # adjust the verbose name or the plural form of it from the Django defaults
    # as django just adding an s to the model name in the admin panel
    class Meta:
        verbose_name_plural = 'Categories'

    name = models.CharField(max_length=254)
    # null equals true and blank equals true so that the friendly name is optional
    friendly_name = models.CharField(max_length=254, null=True, blank=True)

    # create string method to return a name
    def __str__(self):
        return self.name

    # method to return friendly name
    def get_friendly_name(self):
        return self.friendly_name


# create Product model
class Product(models.Model):
    #The first field is a foreign key to the category model. We'll allow this to be null in the database and blank in forms
    # and if a category is deleted we'll set any products that use it to have null for this field rather than deleting the product.
    category = models.ForeignKey('Category', null=True, blank= True, on_delete=models.SET_NULL)
    sku = models.CharField(max_length=254, null=True, blank=True)
    # each product requires a name, a description, and a price, but everything else is optional.
    name = models.CharField(max_length=254)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    rating = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    image_url = models.URLField(max_length=1024, null=True, blank=True)
    image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.name
        