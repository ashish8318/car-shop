from ninja import Router, Query, Body

from utils import AuthBearer
from car_shop.response import ResponseSchema
from shop.models import Shop, Country, City, State
from shop.request import ShopPostSchema, ShopResponseSchema, ShopSchema

router = Router(tags=["Shops"], auth=AuthBearer())

@router.get("shop", response=ResponseSchema)
async def get_shop_details(request,
                           query_filter: ShopSchema = Query(...)):
    """
    **DB query to get shop`s details based on query filter**
    """
    response = ResponseSchema()
    shop = Shop.objects.filter(**query_filter.clean_null()).all().select_related("country", "state", "city")
    data: list = await response.dict_data(schema_model = ShopResponseSchema,
                                          data = shop)
    response.data.extend(data)
    return response

@router.post("shop", response=ResponseSchema)
async def add_shop_details(request,
                           payload: ShopPostSchema = Body(...)):
    """
    **DB query to add new shop`s details**
    """
    response = ResponseSchema()
    try:
        payload.country : Country = await Country.objects.aget(id = payload.country)
    except Country.DoesNotExist:
        response.error.update({"country": "country not find with given id"})
        return response
    
    try:
        payload.state : State = await State.objects.aget(id = payload.state)
    except State.DoesNotExist:
        response.error.update({"state": "state not find with given id"})
        return response
    
    try:
        payload.city : City = await City.objects.aget(id = payload.city)
    except City.DoesNotExist:
        response.error.update({"city": "city not find with given id"})
        return response
    shop = Shop(**payload.dict())
    await shop.asave()
    response.status_code = 201
    response.description = "Shop details successfully added"
    data: list = await response.dict_data(schema_model = ShopResponseSchema,
                                          data = Shop.objects.filter(id = shop.id).all().select_related("country", "state", "city"))
    response.data.extend(data)
    return response

@router.patch("shop", response=ResponseSchema)
async def update_shop_details(request,
                              query_filter: ShopSchema = Query(...),
                              payload: ShopSchema = Body(...)):
    """
    **DB query to update shop`s details based on query filter**
    """
    response = ResponseSchema()
    shop = Shop.objects.filter(**query_filter.clean_null()).all()
    clean_payload: dict = payload.clean_null()
    try:
        if "country" in clean_payload:
            clean_payload["country"] : Country = await Country.objects.aget(id = clean_payload["country"])
    except Country.DoesNotExist:
        response.error.update({"country": "country not find with given id"})
        return response
    
    try:
        if "state" in clean_payload:
            clean_payload["state"] : State = await State.objects.aget(id = clean_payload["state"])
    except State.DoesNotExist:
        response.error.update({"state": "state not find with given id"})
        return response
    
    try:
        if "city" in clean_payload:
            clean_payload["city"] : City = await City.objects.aget(id = clean_payload["city"])
    except City.DoesNotExist:
        response.error.update({"city": "city not find with given id"})
        return response
    
    count: int = await shop.aupdate(**clean_payload)
    data: list = await response.dict_data(schema_model = ShopResponseSchema,
                                    data = Shop.objects.filter(**query_filter.clean_null()).all().select_related("country", "state", "city"))
    response.data.extend(data)
    response.description = f'Total {count} shop`s details updated'
    return response

@router.delete("shop", response=ResponseSchema)
async def delete_shop_records(request,
                              query_filter: ShopSchema = Query(...)):
    """
    **DB query to delete shop`s records based on query filter**
    """
    response = ResponseSchema()
    shop = Shop.objects.filter(**query_filter.clean_null()).all()
    count: tuple = await shop.adelete()
    response.description = f'Total {count[0]} shop`s record deleted'
    return response