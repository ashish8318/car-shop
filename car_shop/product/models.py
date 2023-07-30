from django.db import models
from django.core.validators import MinValueValidator

color_choice = [
                ('read', 'Read'),
                ('black', 'Black'),
                ('green', 'Green'),
                ('blue', 'Blue'),
                ('white', 'White')
            ]

class Car(models.Model):
    name = models.CharField(blank=False, null=False, max_length=250)
    version = models.FloatField(validators=[MinValueValidator(1)])
    price = models.FloatField(validators=[MinValueValidator(1)])
    fuel_type = models.CharField(max_length=100, null=False, choices=[('petrol', 'Petrol'), ('diesel', 'Diesel')])
    milage = models.IntegerField(validators=[MinValueValidator(1)])
    engine = models.CharField(blank=False, null=False, max_length=100)
    transmission = models.CharField(max_length=250)
    seat = models.IntegerField(validators=[MinValueValidator(1)])
    color = models.CharField(max_length=100, null=False, choices=color_choice)
    rate = models.IntegerField(validators=[MinValueValidator(0)])
    power = models.FloatField(validators=[MinValueValidator(1)])
    new_product = models.BooleanField(default=False, blank=False, null=False)
    image_one = models.ImageField(blank=True, null=True, upload_to="car_image")
    image_two = models.ImageField(blank=True, null=True, upload_to="car_image")
    image_three = models.ImageField(blank=True, null=True, upload_to="car_image")
    image_four = models.ImageField(blank=True, null=True, upload_to="car_image")

    def __str__(self) -> str:
        return f'{self.name}'
