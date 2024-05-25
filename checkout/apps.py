from django.apps import AppConfig


class CheckoutConfig(AppConfig):
    # default_auto_field = 'django.db.models.BigAutoField'
    name = 'checkout'

    # Override the ready method and import signals module.
    # so every time a line item is saved or deleted the update_total() model method will be called
    # updating the order_total automatically
    def ready(self):
        import checkout.signals

