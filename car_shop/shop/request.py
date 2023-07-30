from ninja import Schema, ModelSchema

from car_shop.request import BaseQueryFilter
from shop.models import Country, State, City, Shop

class CountrySchema(ModelSchema, BaseQueryFilter):
    """
    Country Schema
    """
    class Config:
        model = Country
        model_fields = ["id", "name", "gst_chrages"]

class StateSchema(ModelSchema, BaseQueryFilter):
    """
    State Schema
    """

    class Config:
        model = State
        model_fields = ["id", "name", "gst_chrages"]

class CitySchema(ModelSchema, BaseQueryFilter):
    """
    City Schema
    """
    class Config:
        model = City
        model_fields = ["id", "name"]

class ShopResponseSchema(ModelSchema, BaseQueryFilter):
    """
    Shop Response Schema
    """
    country: CountrySchema = None
    state: StateSchema = None
    city: CitySchema = None
    class Config:
        model = Shop
        model_fields = ["id", "name", "markerOffset", "coordinates"]

class ShopPostSchema(ModelSchema):
    """
    Shop Post schema for request body
    """
    class Config:
        model = Shop
        model_fields = ["name", "country", "state", "city", "markerOffset", "coordinates"]

class ShopSchema(ModelSchema, BaseQueryFilter):
    """
    Shop schema for query filter and patch request payload
    """
    class Config:
        model = Shop
        model_fields = ["id", "name", "country", "state", "city", "markerOffset", "coordinates"]
        model_fields_optional = ["id", "name", "country", "state", "city", "markerOffset", "coordinates"]