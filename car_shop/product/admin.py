from django.contrib import admin
from product.models import Car

# Register your models here.

class CarAdmin(admin.ModelAdmin):

    list_display = ['name', 'version', 'price', 'fuel_type', 'color']
    search_fields = ['name', 'id']
    list_filter = ['name']

admin.site.register(model_or_iterable=Car, admin_class=CarAdmin)