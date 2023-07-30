from ninja import Router, Query, Body, Form, File
from ninja.files import UploadedFile
from django.db.models import Q

from typing import List

from product.request import CarPostSchema, CarSchema, CarQueryFilterSchema, CarSearchFilterScheam, CarUpdateSchema
from car_shop.response import ResponseSchema
from product.models import Car
from shop.models import Country
from car_shop.logger import logger
from utils import AuthBearer

router = Router(tags=["Product"], auth=AuthBearer())

@router.get("product", response=ResponseSchema)
async def get_car_details(request,
                          query_filter: CarQueryFilterSchema = Query(...)):
    """
    **DB Query to filter car details based on query filter**
    - all query fields are optional
    """
    response = ResponseSchema()
    data: list = await response.dict_data(schema_model = CarSchema,
                                    data = Car.objects.filter(**query_filter.clean_null()).all())
    response.data.extend(data)
    return response

@router.get("product/search", response=ResponseSchema)
async def search_car_details(request,
                             query_filter: CarSearchFilterScheam = Query(...)):
    """
    **DB query to search car details based on query filter**
    - **Query options**
     - search: **param that provide `case sensitive search`, `contains search`, `equal`**
    """
    response = ResponseSchema()
    clean_filter: dict = query_filter.clean_null()
    str_filter = None
    integer_float_filter = None
    if isinstance(clean_filter["search"], str):
        str_filter = Q(name__icontains=clean_filter["search"]) | \
                    Q(engine__icontains = clean_filter["search"]) | \
                    Q(transmission__icontains = clean_filter["search"])
    if isinstance(clean_filter["search"], int) or isinstance(clean_filter["search"], float):
        integer_float_filter = Q(version = clean_filter["search"]) | \
                                Q(milage = clean_filter["search"]) | \
                                Q(seat = clean_filter["search"]) | \
                                Q(rate = clean_filter["search"]) | \
                                Q(power = clean_filter["search"])
        
    if str_filter is not None:
        final_filter = str_filter
    else:
        final_filter = integer_float_filter
    # Removing search key, value from clean_filter 
    del clean_filter["search"]

    car = Car.objects.filter(final_filter, **clean_filter).all()
    
    data: list = await response.dict_data(schema_model = CarSchema,
                              data = car)
    response.data.extend(data)
    return response

@router.get("product/price_calculation", response=ResponseSchema)
async def get_car_price_calculation_data(request):
    """
    **DB query to get car price calculation data**
    """
    response = ResponseSchema()
    gst_chrages_result = []
    async for country in Country.objects.all():
        async for state in country.state.all():
            gst_chrages_result.append({state.name: state.gst_chrages + country.gst_chrages})
    response.data.extend(gst_chrages_result)
    return response

@router.post("product", response=ResponseSchema)
async def add_car_details(request,
                          payload: CarPostSchema = Form(...),
                          product_images: List[UploadedFile] = File(...)):
    """
    **DB query to add new car details**
    - all fields are required
    """
    response = ResponseSchema()
    car: Car = Car(**payload.dict())
    if len(product_images) < 4:
        response.error.update({"product_image": "please upload 4 images"})
        return response
    
    for file in product_images:
        if file.content_type not in ["image/jpeg", "image/jpg", "image/png"]:
            response.error.update({"product_image": f"does not support given file type: {file.content_type}"})
            return response
        
    # Initlizating images from list of image 
    car.image_one = product_images[0]
    car.image_two = product_images[1]
    car.image_three = product_images[2]
    car.image_four = product_images[3]

    # await car.asave()
    data: list = await response.dict_data(schema_model = CarSchema,
                                          data = Car.objects.aget(pk=car.id))
    response.data.extend(data)
    response.status_code = 201
    response.description = "Car details successfuly added"
    return response

@router.post("product/update", response=ResponseSchema)
async def update_car_details(request,
                             query_filter: CarQueryFilterSchema = Query(...),
                             payload: CarUpdateSchema = Form(...),
                             image1: UploadedFile = File(default=None),
                             image2: UploadedFile = File(default=None),
                             image3: UploadedFile = File(default=None),
                             image4: UploadedFile = File(default=None)):
    """
    **DB query to updated car details based on query filter**
    - all payload fields are optional
    - all query fields are optional
    """
    response = ResponseSchema()
    clean_payload = payload.clean_empty()
    Sequence = ("one", "two", "three", "four") 
    for index, item in enumerate([image1, image2, image3, image4]):
        if item is not None:
            if item.content_type not in ["image/jpeg", "image/jpg", "image/png"]:
                response.error.update({"product_image": f"does not support given image1 type: {item.content_type}"})
                return response
            clean_payload[f"image_{Sequence[index]}"] = item
    
    cars = Car.objects.filter(**query_filter.clean_null()).all()
    # count: int = await cars.aupdate(***clean_payload)
    # note this method not use for image of file field because does not call obj.save method
    async for car in cars:
        car.__dict__.update(**clean_payload)
        await car.asave()

    data: list = await response.dict_data(schema_model = CarSchema,
                                    data = Car.objects.filter(**query_filter.clean_null()).all())
    response.data.extend(data)
    response.description = f'Total {len(response.data)} car details updated'
    return response

@router.delete("product")
async def delete_car_details(request,
                             query_filter: CarQueryFilterSchema = Query(...)):
    """
    **DB query to delete car detaisl based on query filter**
    - all query fields are optional
    """
    response = ResponseSchema()
    result: tuple = await Car.objects.filter(**query_filter.clean_null()).all().adelete()
    response.description = f"Total {result[0]} records deleted"
    logger.warning("fTotal {result[0]} records deleted")
    return response