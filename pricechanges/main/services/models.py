from pydantic import BaseModel, model_validator
from typing import Self


class Item(BaseModel):
    marketplace: str
    id: int
    brand: str
    name: str
    rating: float
    feedbacks: int
    volume: int
    price: int
    item_url: str

    @model_validator(mode='after')
    def convert_price(self) -> Self:
        if self.marketplace == 'wb' and self.volume == 0 and self.price == -1:
            self.name = 'Наименование не определено'
            self.rating = -1
            self.feedbacks = -1
            self.volume = -1
            return self
        if self.price is not None and self.marketplace == 'wb':
            self.price = int(self.price / 98)
            return self
        return self
