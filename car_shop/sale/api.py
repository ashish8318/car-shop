from django.contrib.auth.models import User
from ninja import Router, Query, Body
from typing import Union
import calendar

from sale.request import SalesPostSchema, SalesSchema, SalseResponseSchema, SalesGraphSchema
from car_shop.response import ResponseSchema
from product.models import Car
from sale.models import Order
from utils import AuthBearer

router = Router(tags=["Sales"], auth=AuthBearer())

@router.get("sales", response=ResponseSchema)
async def get_sales_details(request, query_filter: SalesSchema = Query(...)):
    """
    **DB query to get order details based on query filter**
    """
    response = ResponseSchema()
    orders = Order.objects.filter(**query_filter.clean_null()).select_related("car", "customer")
    data: list = await response.dict_data(schema_model = SalseResponseSchema,
                                          data = orders)
    response.data.extend(data)
    print(query_filter.clean_null())
    return response

@router.get("sales/graph", response=ResponseSchema)
async def get_graph_data(request):
    """
    **DB query for sales graph data**
    """
    response = ResponseSchema()
    cars = Car.objects.all()
    async for car in cars:
        sales_graph_response: SalesGraphSchema = SalesGraphSchema(label = car.name)
        for month_number in range(1, 13):
            count: int = await car.order.filter(order_date__month = month_number).acount()
            sales_graph_response.data.append({calendar.month_name[month_number]: count})
        response.data.append(sales_graph_response.dict())
    return response


@router.post("sales", response=ResponseSchema)
async def add_order_details(request, payload: SalesPostSchema = Body(...)):
    """
    **DB query to add new order details**
    """
    response = ResponseSchema()
    clean_dict: dict = payload.clean_null()
    try:
        clean_dict["car"]: Union[Car, None] = await Car.objects.aget(id = clean_dict.get("car"))
    except Car.DoesNotExist:
        response.status_code = 400
        response.error.update({"car": "car not find with given id"})
        return response
    try:
        clean_dict["customer"]: Union[User, None] = await User.objects.aget(id = clean_dict.get("customer"))
    except User.DoesNotExist:
        response.status_code = 400
        response.error.update({"user": "user not find with given id"})
        return response
    order: Order = Order(**clean_dict)
    await order.asave()
    data: list = await response.dict_data(schema_model = SalseResponseSchema,
                                         data = Order.objects.filter(id = order.id).select_related("car", "customer"))
    response.status_code = 201
    response.data.extend(data)
    response.description = "Sales details successfuly added"
    return response

@router.patch("sales", response=ResponseSchema)
async def update_order_details(request,
                               query_filter: SalesSchema = Query(...),
                               payload: SalesSchema = Body(...)):
    """
    **DB query to update seles details based on query filter**
    """
    response = ResponseSchema()
    orders = Order.objects.filter(**query_filter.clean_null()).all()
    clean_payload: dict = payload.clean_null()
    try:
        if "car" in clean_payload:
            clean_payload["car"]: Union[Car, None] = await Car.objects.aget(id = clean_payload.get("car"))
    except Car.DoesNotExist:
        response.status_code = 400
        response.error.update({"car": "car not find with given id"})
        return response
    try:
        if "customer" in clean_payload:
            clean_payload["customer"]: Union[User, None] = await User.objects.aget(id = clean_payload.get("customer"))
    except User.DoesNotExist:
        response.status_code = 400
        response.error.update({"user": "user not find with given id"})
        return response
    count = await orders.aupdate(**clean_payload)
    data: list = await response.dict_data(schema_model = SalseResponseSchema,
                                          data = Order.objects.filter(**query_filter.clean_null()).all().select_related("car", "customer"))
    response.data.extend(data)
    response.description = f'Total {count} sales details updated'
    return response

@router.delete("sales", response=ResponseSchema)
async def delete_order_details(request,
                               query_filter: SalesSchema = Query(...)):
    """
    **DB query to delete sales details based on query filter**
    """
    response = ResponseSchema()
    orders = Order.objects.filter(**query_filter.clean_null()).all()
    count: tuple = await orders.adelete()
    response.description = f'Total {count[0]} sales details deleted'
    return response
