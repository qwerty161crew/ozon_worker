from pydantic import BaseModel


class ProductType(BaseModel):
    product_name: str


class Product(BaseModel):
    product_name: str
    ozon_id: str
    product_type: list
    description: str | None
    price: float | None
    full_price: float | None
    rating: float | None
