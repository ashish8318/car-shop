from django.db import models
from django.core.validators import MinValueValidator

class Country(models.Model):
    """
    model for store country records
    """
    name = models.CharField(max_length=250, blank=False, null=False)
    gst_chrages = models.FloatField(blank=False, null=False, default=0, validators=[MinValueValidator(0)])

    def __str__(self)-> str:
        return f'{self.name}'
    
class State(models.Model):
    """
    model for store state records
    """
    name = models.CharField(max_length=250, blank=False, null=False)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="state")
    gst_chrages = models.FloatField(blank=False, null=False, default=0, validators=[MinValueValidator(0)])

    def __str__(self)-> str:
        return f'{self.name}'
    
class City(models.Model):
    """
    model for store city records
    """
    name = models.CharField(max_length=250, blank=False, null=False)
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name="city")

    def __str__(self)-> str:
        return f'{self.name}'
    
class Shop(models.Model):
    """
    models for shop details
    """
    name = models.CharField(max_length=250, blank=False, null=False)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="shop_country")
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name="shop_state")
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="shop_city")
    markerOffset = models.FloatField(blank=False, null=False)
    coordinates = models.CharField(blank=False, null=False)

    def __str__(self):
        return f'{self.name}'