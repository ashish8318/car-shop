from django.contrib import admin
from shop.models import Country, State, City, Shop

class ShopAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "country", "state", "city", "markerOffset", "coordinates"]
    list_filter = ["country", "state", "city"]
    search_fields = ["name", "id"]

admin.site.register(model_or_iterable=Shop, admin_class=ShopAdmin)
admin.site.register(model_or_iterable=Country)
admin.site.register(model_or_iterable=State)
admin.site.register(model_or_iterable=City)

