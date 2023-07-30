from datetime import datetime
from django.utils import timezone
from ninja import ModelSchema, Schema
from typing import List

from car_shop.request import BaseQueryFilter, PaymentMethod, PaymentStatus
from product.request import CarSchema
from user.request import UserSchema
from sale.models import Order

class SalesPostSchema(ModelSchema, BaseQueryFilter):
    """
    order request body payload 
    """
    payment_method: PaymentMethod
    payment_status: PaymentStatus
    class Config:
        model = Order
        model_fields = ["car", "customer", "payment_method", "payment_status", "order_date"]

class SalesSchema(ModelSchema, BaseQueryFilter):
    """
    order query filter schema
    """
    payment_method: PaymentMethod = None
    payment_status: PaymentStatus = None
    order_date: datetime = None
    class Config:
        model = Order
        model_fields = ["id", "car", "customer"]
        model_fields_optional = ["id", "car", "customer"]

class SalseResponseSchema(Schema):
    """
    Order Response Schema
    """
    id: int
    car: CarSchema = None
    customer: UserSchema = None
    payment_method: str
    payment_status: str
    order_date: datetime

class SalesGraphSchema(Schema):
    """
    Sales Graph Schema
    """
    label: str = None
    data: List = []

