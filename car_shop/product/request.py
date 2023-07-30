from ninja import ModelSchema, Schema
from typing import Union

from product.models import Car
from car_shop.request import Color, FuelType
from car_shop.request import BaseQueryFilter

class CarPostSchema(ModelSchema):
    """ 
    car request body payload schema
    """

    class Config:
        model = Car
        model_fields = "__all__"
        model_exclude = ["id", "image_one", "image_two", "image_three", "image_four"]

class CarUpdateSchema(ModelSchema, BaseQueryFilter):
    """ 
    car patch request body schema
    """
    # Overiding fields value with 0 because post not support None value for int field
    version: int = 0
    price: int = 0
    milage: int = 0
    seat: int = 0
    rate: int = 0
    power: int = 0

    class Config:
        model = Car
        model_fields = "__all__"
        model_exclude = ["id", "image_one", "image_two", "image_three", "image_four"]
        model_fields_optional = "__all__"

    def clean_empty(self):
            return {key: value for (key, value) in self.dict().items() if value is not '' and value is not 0}
     
class CarSchema(ModelSchema):
    """ 
    car schema
    """
    class Config:
        model = Car
        model_fields = "__all__"
        model_fields_optional = "__all__"

class CarQueryFilterSchema(ModelSchema, BaseQueryFilter):
    """ 
    car query filter schema
    """
    color: Color = None
    fuel_type: FuelType = None

    class Config:
        model = Car
        model_fields = "__all__"
        model_fields_optional = "__all__"

class CarSearchFilterScheam(BaseQueryFilter):
    """
    Car Search Schema
    """
    search: Union[str, int, float]
    color: Color = None
    fuel_type: FuelType = None
    price: float = None