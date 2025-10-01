from datetime import datetime, time, timedelta
from uuid import UUID
from enum import Enum
from typing import Annotated, Any, Literal
from fastapi import Body, Cookie, FastAPI, Form, Header, Path, Query, Response, status
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel, EmailStr, Field

class SignUp(BaseModel):
    username: str
    password: str

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    pass

class UserDB(UserBase):
    hashed_pwd: str


class CardDataType(str, Enum):
    data1 = "DATA1"
    data2 = "DATA2 "
    data3 = "DATA3"

class Image(BaseModel):
    name: str
    url: str

class Item(BaseModel):
    name: str = Field(description="Name or title for the item", title="Item title", max_length=255, examples=["Oneplus nord 3 earbuds pro", "Boat Airdopes pro"])
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

def fake_pwd_hash(plain_passwd:str):
    return "secret" + plain_passwd

def fake_db_save(user: UserCreate):
    hashed_pwd = fake_pwd_hash(user.password)
    user_in_db = UserDB(**user.model_dump(), hashed_pwd=hashed_pwd)
    print("User saved to DB")
    return user_in_db


app = FastAPI()



@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/users", response_model=UserResponse)
async def sign_up(user: UserCreate) -> Any:
    user_saved = fake_db_save(user)
    return user_saved

@app.get("/items", response_model=list[Item])
async def get_items(filter_query: Annotated[FilterParams, Query()]) -> Any:
    return [{"name": "Portal Gun", "price": 42.0},
        {"name": "Plumbus", "price": 32.0},
]

@app.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: Annotated[int, Path(ge=1, title="The ID of item", description="The ID of item for which details is to be retrieved")], 
                   q: Annotated[str | None, Query(max_length=50, description="Keywords to look for in item")] = None) -> Any:
        return {"name": "Plumbus", "price": 32.0}

@app.get("/cards/{card_data}")
async def get_card(card_data: CardDataType):
    return {
            "request_type": card_data
    }

@app.get("/files/{file_path:path}")
async def get_files(file_path: str):
    return {"file_path": file_path}

@app.post("/items", status_code=status.HTTP_201_CREATED)
async def create_item(item: Item):
    item_dict = item.model_dump()
    if item.tax is not None:
        price_with_tax = item.tax + item.price
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict

@app.put("/items/{item_id}")
async def update_item(item_id: UUID, 
                      start_datetime: Annotated[datetime, Body()],
                      end_datetime: Annotated[datetime, Body()],
                      process_after: Annotated[timedelta, Body()],
                      repeat_at: Annotated[time | None, Body()] = None
                      ):
    return {"item_id": item_id, "start_datetime": start_datetime, "end_datetime": end_datetime, "process_after": process_after, "repeat_at": repeat_at}

@app.get("/offer")
async def get_offers(user_agent: Annotated[str | None, Header()] = None):
    return {"User-Agent": user_agent}

@app.get("/teleport")
async def get_portal(teleport: bool = False) -> Response:
    if teleport:
        return RedirectResponse(url="http://localhost:8000/items")
    else:
        return JSONResponse(content={"message": "Here is your interdimensional portal"})

# Sign up
@app.post("/sign-up", status_code=status.HTTP_201_CREATED)
async def create_account(signup: Annotated[SignUp, Form()]):
    return {"message": "Account created"}


