import base64
import json
import logging
from datetime import datetime
from io import BytesIO
from typing import Optional, List

from PIL import Image
from fastapi import FastAPI, Depends, UploadFile, HTTPException, File, Body, Form
from motor import motor_asyncio
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request

MONGO_DETAILS = "mongodb://mongo:27017/bot"

client = motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
database = client.bot
order_collection = database.get_collection("order_collection")

app = FastAPI(
    upload_max_size="100MB",
    max_request_size=1024 * 1024 * 1024
)


class Item(BaseModel):
    name: Optional[str]
    count: Optional[int]
    price: Optional[float]


class Order(BaseModel):
    to: str
    deadline: datetime = datetime.now()
    name: Optional[str] = None
    client: Optional[str] = None
    communication: Optional[str] = None
    prepayment: Optional[str] = None
    delivery: Optional[str] = None
    address: Optional[str] = None
    comment: Optional[str] = None
    items: Optional[str] = None
    created_at: Optional[datetime] = datetime.now()


logging.basicConfig(level=logging.DEBUG)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger = logging.getLogger("uvicorn")

    # Логирование метода запроса и URL
    logger.info(f"Request: {request.method} {request.url}")

    # Логирование заголовков
    headers = dict(request.headers)
    logger.info(f"Headers: {json.dumps(headers, indent=2)}")

    # Логирование тела запроса
    body = await request.body()
    logger.info(f"Body: {body.decode('utf-8')}")

    response = await call_next(request)

    # Логирование статуса ответа
    logger.info(f"Response status: {response.status_code}")

    return response


@app.post("/order")
async def post_order(
    to: str = Form(),
    deadline: datetime = Form(default=datetime.now()),
    name: Optional[str] = Form(default=None),
    client: Optional[str] = Form(default=None),
    communication: Optional[str] = Form(default=None),
    prepayment: Optional[str] = Form(default=None),
    delivery: Optional[str] = Form(default=None),
    address: Optional[str] = Form(default=None),
    comment: Optional[str] = Form(default=None),
    items: Optional[str] = Form(default=None),
    created_at: Optional[datetime] = Form(default=datetime.now()),
    images: List[UploadFile] = File(default=None),
):

    order = Order(
        to=to,
        deadline=deadline,
        name=name,
        client=client,
        communication=communication,
        prepayment=prepayment,
        delivery=delivery,
        address=address,
        comment=comment,
        items=items,
        created_at=created_at,
    )

    # images = []
    if images and len(images) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 images allowed")

    images_data = []
    if images:
        for image in images:
            image_data = await image.read()
            img_base64 = base64.b64encode(image_data).decode('utf-8')
            images_data.append(img_base64)

    order_data = order.model_dump()
    order_data["images"] = images_data

    inserted_order = await order_collection.insert_one(order_data)

    return {"id": str(inserted_order.inserted_id)}

# @app.post("/order")
# async def post_order(
#     to: str = Form(...),
#     deadline: str = Form(...),
#     name: Optional[str] = Form(None),
#     client: Optional[str] = Form(None),
#     communication: Optional[str] = Form(None),
#     prepayment: Optional[str] = Form(None),
#     delivery: Optional[str] = Form(None),
#     address: Optional[str] = Form(None),
#     comment: Optional[str] = Form(None),
#     items: str = Form(...),  # Items as JSON string
#     images: List[UploadFile] = File(None)
# ):
#     if images and len(images) > 10:
#         raise HTTPException(status_code=400, detail="Maximum 10 images allowed")
#
#     images_data = []
#     if images:
#         for image in images:
#             image_data = await image.read()
#             img_base64 = base64.b64encode(image_data).decode('utf-8')
#             images_data.append(img_base64)
#
#     items_list = json.loads(items)  # Parse items JSON string
#     item_objects = [Item(**item) for item in items_list]
#
#     order_data = {
#         "to": to,
#         "deadline": deadline,
#         "name": name,
#         "client": client,
#         "communication": communication,
#         "prepayment": prepayment,
#         "delivery": delivery,
#         "address": address,
#         "comment": comment,
#         "items": item_objects,
#         "created_at": datetime.now(),
#         "images": images_data
#     }
#
#     inserted_order = await order_collection.insert_one(order_data)
#
#     return {"id": str(inserted_order.inserted_id)}
