from ninja import NinjaAPI

from product.api import router as product_router
from user.api import router as user_router
from sale.api import router as sales_router
from shop.api import router as shop_router

api = NinjaAPI(
    title = "Car Shop",
    description = "Car Shop Management",
    urls_namespace="api"
)

api.add_router("/", router = product_router)
api.add_router("/", router = user_router)
api.add_router("/", router = sales_router)
api.add_router("/", router = shop_router)