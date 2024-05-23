import asyncio
import base64
import json
import logging
import sys
from datetime import datetime
from io import BytesIO
from typing import Dict

from aiogram import Dispatcher, Bot, types
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message, InputFile, BufferedInputFile, InputMediaPhoto
from aiogram.utils.payload import decode_payload
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from motor import motor_asyncio


MONGO_DETAILS = "mongodb://mongo:27017/bot"
# MONGO_DETAILS = "mongodb://localhost:27017"

client = motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

database = client.bot

user_collection = database.get_collection("users_collection")
order_collection = database.get_collection("order_collection")


TOKEN = "6840739601:AAEM6oMDbD7FqO9LsKdMZzn7tXhSeUQU3Ns"
# TOKEN = "7105828267:AAGlYANgVAHiUbDg2Zq7t6e2-5_MiEGIYB8"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot)


def order_to_text(order: Dict) -> str:
    # try:
    order_text = f"Новый заказ: \n"
    order_text += f"Название: {order.get("name")}\n"
    order_text += f"Состав:\n"
    for item in json.loads(order.get("items")):
        order_text += f"\t- Имя: {item.get("name")}"
        order_text += f"\t- Кол-во: {item.get("count")}"
        order_text += f"\t- Цена: {item.get("price")}"
    order_text += f"Предоплата: {order.get("prepayment")}\n"
    order_text += f"Клиент: {order.get("client")}\n"
    order_text += f"Доставка: {order.get("delivery")}\n"
    order_text += f"Адрес: {order.get("address")}\n"
    order_text += f"Комментарий: {order.get("comment")}\n"
    order_text += f"Связь: {order.get("communication")}\n"
    order_text += f"Создан: {order.get("created_at")}\n"
    return order_text


# except Exception as e:
#     return order.__str__()


async def send_orders():
    try:
        orders = await order_collection.find({}).to_list(None)
        for order in orders:
            order_text = order_to_text(order)

            images_base64 = order.get("images", [])
            media_group = []
            for image_base64 in images_base64:
                image_bytes = base64.b64decode(image_base64)
                media_group.append(
                    InputMediaPhoto(media=BufferedInputFile(file=image_bytes, filename="f"), caption=order_text[:1000]))
            for user in await user_collection.find({}).to_list(None):
                if order["to"] == user["cms_id"]:
                    chat_id = user["chat_id"]
                    try:
                        print(f"chat_id:{chat_id}")
                        if len(media_group) > 0:
                            await bot.send_media_group(chat_id, media=media_group)
                        else:
                            await bot.send_message(chat_id, order_text[:4000])
                    except TelegramAPIError as e:
                        print(f"Failed to send message to chat_id {chat_id}: {e}")
            await order_collection.delete_one({"_id": order["_id"]})
    except Exception as e:
        print(f"An error occurred while sending orders: {e}")


@dp.message(CommandStart(deep_link=True))
async def command_start_handler(message: Message, command: CommandObject) -> None:
    args = command.args
    # payload = decode_payload(args)
    user = await user_collection.find_one({"chat_id": message.from_user.id})
    if user is None:
        await user_collection.insert_one({"cms_id": args, "chat_id": message.from_user.id})
    await message.answer("Hello!")


async def main() -> None:
    scheduler = AsyncIOScheduler()

    scheduler.add_job(send_orders, 'interval', seconds=10)
    scheduler.start()

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
