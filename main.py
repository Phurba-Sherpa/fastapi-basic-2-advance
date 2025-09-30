import random
from enum import Enum
from typing import Annotated, Literal
from fastapi import Body, FastAPI, Path, Query
from pydantic import AfterValidator, BaseModel, Field

class CardDataType(str, Enum):
    data1 = "DATA1"
    data2 = "DATA2 "
    data3 = "DATA3"

class Image(BaseModel):
    name: str
    url: str

class Item(BaseModel):
    name: str
    desc: str | None = None
    price: float
    tax: float | None = None
    tag: set[str] = set()
    image: Image | None = None
    

class Offer(BaseModel):
    name: str
    desc: str |  None  = None
    price: float
    items: list[Item]

class FilterParams(BaseModel):
    limit: int = Field(10, gt=0, le=100, description="Records count per request")
    offset: int = Field(1, ge=1, description="Current index of record")
    order_by: Literal["created_at", "updated_at"] = "updated_at"
    tags: list[str] = []

data = {
    "isbn-9781529046137": "The Hitchhiker's Guide to the Galaxy",
    "imdb-tt0371724": "The Hitchhiker's Guide to the Galaxy",
    "isbn-9781439512982": "Isaac Asimov: The Complete Stories, Vol. 2",
}

def check_valid_id(id: str):
    if not id.startswith(('isbn-', 'imdb-')):
        raise ValueError('Invalid ID format, it must start with "isbn-" or "imdb-"')
    return id

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}



@app.get("/items")
async def get_items(filter_query: Annotated[FilterParams, Query()]):
    return filter_query

@app.get("/items/{item_id}")
async def get_item(item_id: Annotated[int, Path(ge=1, title="The ID of item", description="The ID of item for which details is to be retrieved")], 
                   q: Annotated[str | None, Query(max_length=50, description="Keywords to look for in item")] = None):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results

@app.get("/cards/{card_data}")
async def get_card(card_data: CardDataType):
    return {
            "request_type": card_data
    }

@app.get("/files/{file_path:path}")
async def get_files(file_path: str):
    return {"file_path": file_path}

@app.post("/items")
async def create_item(item: Item):
    item_dict = item.model_dump()
    if item.tax is not None:
        price_with_tax = item.tax + item.price
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict

@app.put("/items/{item_id}")
async def update_item(item_id: str, item: Item):
    return {"item_id": item_id, "item": item}

@app.get("/offer")
async def get_offers(offer:Offer):
    return offer
