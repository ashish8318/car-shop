from django.db.models.fields.files import ImageField
from django.db.models import Model

from ninja.schema import Schema
from typing import List, AsyncIterable

class ResponseSchema(Schema):
    status_code: int = 200
    error: dict = {}
    description: str = None
    data: List[dict] = []

    def is_iterable(self, obj):
        if isinstance(obj, AsyncIterable):
            return True
        else:
            return False
    
    def get_full_image_path(self,
                            schema_model: Schema,
                            obj: Model)-> dict:
        """
        get table instance and generate pull path for image field
        """
        dict_data = schema_model.from_orm(obj).dict()
        model_fields = obj.__class__._meta.get_fields()
        for field in model_fields:
            # Check if the field is of type ImageField
            if isinstance(field, ImageField):
                # Access the field name and value
                field_name = field.name
                if getattr(obj, field_name) is not None:
                    dict_data[field_name] = f"http://localhost:8000{getattr(obj, field_name).url}"
        return dict_data

    async def dict_data(self,
                        schema_model: Schema, 
                        data):
        """ 
        convert orm model/ query object to dict
        """

        if self.is_iterable(data):
            return [self.get_full_image_path(schema_model=schema_model, obj=item) async for item in data]
        else:
            result = []
            temp = await data
            if temp is not None:
                result.append(schema_model.from_orm(temp).dict())
                return result
            else:
                return result