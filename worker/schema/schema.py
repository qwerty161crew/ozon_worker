from pydantic import BaseModel


class Product(BaseModel):
    product_name: str
    ozon_id: str
    product_type: list
    description: str | None
    price: float | None
    full_price: float | None
    rating: float | None
