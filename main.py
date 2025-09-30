import random
from enum import Enum
from typing import Annotated
from fastapi import FastAPI, Query
from pydantic import AfterValidator, BaseModel

class CardDataType(str, Enum):
    data1 = "DATA1"
    data2 = "DATA2 "
    data3 = "DATA3"

class Item(BaseModel):
    name: str
    desc: str | None = None
    price: float
    tax: float | None = None
    

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
async def get_items(
    id: Annotated[str | None, AfterValidator(check_valid_id)] = None,
    offset: Annotated[int, Query(ge=1,description="Current page number from which records are to be fetched")] = 1, 
    limit: Annotated[int, Query(ge=1, le=100, description="Number of records per request")] = 10,
    q: Annotated[str | None, Query(max_length=50, deprecated=True, description="Query strong for the items to search in the database that have a good match")] = None):
    if id:
        item = data.get(id)
    else:
        id, item = random.choice(list(data.items()))
    return {"id": id, "name": item}

@app.get("/items/{item_id}")
async def get_item(item_id: int):
    return {"item_id": item_id}

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
