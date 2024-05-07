import base64
from datetime import datetime
from io import BytesIO

from PIL import Image
from fastapi import FastAPI, Depends, UploadFile, HTTPException
from motor import motor_asyncio
from pydantic import BaseModel
from bson import ObjectId

MONGO_DETAILS = "mongodb://mongo:27017"

client = motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
database = client.bot
order_collection = database.get_collection("order_collection")


class Order(BaseModel):
    name: str
    images: list[UploadFile]  # Changed to list of UploadFile for multiple images
    price: str
    prepayment: str
    compound: str
    client: str
    delivery: str
    address: str
    comment: str


app = FastAPI()


@app.post("/order")
async def post_order(order: Order = Depends(Order)):
    if len(order.images) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 images allowed")

    images_data = []
    for image in order.images:
        image_data = await image.read()
        img_base64 = base64.b64encode(image_data).decode('utf-8')
        images_data.append(img_base64)

    created_at = datetime.now()
    order_data = order.dict()
    order_data["images"] = images_data
    order_data["created_at"] = created_at
    inserted_order = await order_collection.insert_one(order_data)

    return {"id": str(inserted_order.inserted_id)}
