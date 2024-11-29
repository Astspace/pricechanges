from pydantic import BaseModel, field_validator

class Item(BaseModel):
    id: int
    brand: str
    name: str
    rating: float
    feedbacks: int
    volume: int
    price: int

    @field_validator("price")
    def convert_price(cls, price: int) -> float:
        if price is not None:
            return price / 100