import base64
from datetime import datetime
from io import BytesIO
from typing import Optional, List

from PIL import Image
from fastapi import FastAPI, Depends, UploadFile, HTTPException
from motor import motor_asyncio
from pydantic import BaseModel
from bson import ObjectId

MONGO_DETAILS = "mongodb://mongo:27017/bot"

client = motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
database = client.bot
order_collection = database.get_collection("order_collection")


class Item(BaseModel):
    name: Optional[str]
    count: Optional[int]
    price: Optional[float]


class Order(BaseModel):
    to: str
    deadline: str
    name: Optional[str] = None
    client: Optional[str] = None
    communication: Optional[str] = None
    images: Optional[list[UploadFile]] = []
    prepayment: Optional[str] = None
    delivery: Optional[str] = None
    address: Optional[str] = None
    comment: Optional[str] = None
    items: Optional[List[Item]] = []
    created_at: Optional[datetime] = datetime.now()


app = FastAPI(
    upload_max_size="100MB",
    max_request_size=1024 * 1024 * 1024
)


@app.post("/order")
async def post_order(order: Order = Depends(Order)):
    if len(order.images) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 images allowed")

    images_data = []
    for image in order.images:
        image_data = await image.read()
        img_base64 = base64.b64encode(image_data).decode('utf-8')
        images_data.append(img_base64)
    order_data = order.dict()
    order_data["images"] = images_data
    inserted_order = await order_collection.insert_one(order_data)

    return {"id": str(inserted_order.inserted_id)}
