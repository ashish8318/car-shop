from django.contrib import admin

from sale.models import Order

class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'car', 'customer', 'payment_method', 'payment_status', 'order_date']
    list_filter = ['order_date', 'payment_status', 'id']
    search_fields = ['id', 'payment_status', 'order_date', 'payment_method']
    

admin.site.register(model_or_iterable=Order, admin_class=OrderAdmin)
