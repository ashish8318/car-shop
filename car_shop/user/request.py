from django.contrib.auth.models import User
from ninja import Schema, ModelSchema

from car_shop.request import BaseQueryFilter

class TestDrivePostSChema(Schema):
    """ 
    Request payload for test drive 
    """
    username: str
    email: str
    password: str

class TestDriveSchema(BaseQueryFilter):
    """ 
    Schema for query filter test drive and returns response
    """
    username: str = None
    email: str = None

class UserSchema(ModelSchema):
    """
    django auth user schema 
    """
    class Config:
        model = User
        model_fields = ["username", "email"]

class UserSignInSchema(ModelSchema):
    """
    user sign-in schema
    """

    class Config:
        model = User
        model_fields = ["username", "email", "password"]
class UserLoginSchema(ModelSchema):
    """
    User login Schema
    """

    class Config:
        model = User
        model_fields = ["email", "password"]

class UserChangePassword(Schema):
    """
    Change User Password
    """

    email: str
    password: str
    conform_password: str

class GoogleSocialAuthSchema(Schema):
    """
    Get token to validate token after getting access token from google
    """

    token: str

class UserUpdateSchema(Schema):
    """
    Update user details schema
    """
    username: str = None
    email: str = None
    password: str = None

    def clean_empty(self):
        return {key: value for (key, value) in self.dict().items() if value is not ''}