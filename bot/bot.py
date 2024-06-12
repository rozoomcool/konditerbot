import asyncio
import base64
import json
import logging
import sys
from typing import Dict

import pymongo
from aiogram import Dispatcher, Bot, types
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message, InputFile, BufferedInputFile, InputMediaPhoto
from aiogram.utils.payload import decode_payload
from apscheduler.schedulers.asyncio import AsyncIOScheduler

MONGO_DETAILS = "mongodb://mongo:27017/bot"
# MONGO_DETAILS = "mongodb://localhost:27017"

client = pymongo.MongoClient(MONGO_DETAILS)

database = client.bot

user_collection = database.get_collection("users_collection")
order_collection = database.get_collection("order_collection")

TOKEN = "6840739601:AAEM6oMDbD7FqO9LsKdMZzn7tXhSeUQU3Ns"
# TOKEN = "7105828267:AAGlYANgVAHiUbDg2Zq7t6e2-5_MiEGIYB8"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot)


def order_to_text(order: Dict) -> str:
    # try:
    order_text = f"Новый заказ✅\n\n"
    order_text += f"Название: {order.get("name")}\n"
    try:
        order_text += f"Сумма заказа: {sum(item.price for item in order.get("items") if order.get("items") is not None)}\n"
    except Exception as e:
        order_text += f"Сумма заказа: _"
    try:
        items = json.loads(order.get("items") if order.get("items") is not None else "[]")
        logging.info(f"ITEMS::: {items}")
        order_text += f"\n\nСостав заказа:\n"
        for item in items:
            # order_text += "\n"
            order_text += f"\nИмя: {item.get("name")}"
            order_text += f"\nНачинка: {item.get("filling") if item.get("filling") is not None else '_'}"
            order_text += f"\nКол-во: {item.get("count")}"
            order_text += f"\nЦена: {item.get("price")}"
    except Exception as e:
        # order_text += f"\nСостав: {order.get("items")}"
        logging.error(f"{e}")
        pass
    order_text += f"\nПредоплата: {order.get("prepayment")}\n"
    order_text += f"Клиент: {order.get("client")}\n"
    order_text += f"Доставка: {order.get("delivery")}\n"
    order_text += f"Адрес: {order.get("address")}\n"
    order_text += f"Комментарий: {order.get("comment")}\n"
    order_text += f"\nТелефон: {order.get("communication")}\n"
    order_text += f"\nСоздан: {order.get("created_at").strftime("%Y-%m-%d %H") if order.get("created_at") is not None else '_'}\n"
    order_text += f"Срок до: {order.get("deadline").strftime("%Y-%m-%d %H") if order.get("deadline") is not None else '_'}\n"

    return order_text


# except Exception as e:
#     return order.__str__()


async def send_orders():
    try:
        orders = list(order_collection.find({}))
        print(f":::::start")
        for order in orders:
            try:
                print(":::::orders")
                order_text: str
                order_text = order_to_text(order)

                images_base64 = order.get("images", [])
                media_group = []
                print(":::::media")
                for image_base64 in images_base64:
                    print(":::::images")
                    image_bytes = base64.b64decode(image_base64)
                    # media_group.append(
                    #     InputMediaPhoto(media=BufferedInputFile(file=image_bytes, filename="f"), caption=order_text[:1000]))
                    media_group.append(
                        InputMediaPhoto(media=BufferedInputFile(file=image_bytes, filename="f"), ))
                # for user in await user_collection.find({}).to_list(None):
                for user in user_collection.find({}):
                    if order["to"] == user["cms_id"]:
                        chat_id = user["chat_id"]
                        try:
                            print(f"chat_id:{chat_id}")
                            if len(media_group) > 0:
                                await bot.send_media_group(chat_id, media=media_group)
                            await bot.send_message(chat_id, order_text[:4000])
                        except TelegramAPIError as e:
                            print(f"Failed to send message to chat_id {chat_id}: {e}")
            except Exception as e:
                print(f"Error process order: {e}")
            finally:
                order_collection.delete_one({"_id": order["_id"]})
    except Exception as e:
        print(f"An error occurred while sending orders: {e}")


text = """
Привет! Я — бот My Cake.

Я буду сюда дублировать заказы из приложения, чтобы список заказов всегда был в доступе.

Как только ты внесешь первый заказ в приложение – я сразу же пришлю его сюда👍🏻
"""


@dp.message(CommandStart(deep_link=True))
async def command_start_handler(message: Message, command: CommandObject) -> None:
    args = command.args
    # payload = decode_payload(args)
    user = user_collection.find_one({"chat_id": message.from_user.id})
    if user is None:
        entity = user_collection.insert_one({"cms_id": args, "chat_id": message.from_user.id})
        user = user_collection.find_one({"chat_id": message.from_user.id})
        await message.answer(f"{text}\nВаш id: {user.get("cms_id")}")
    await message.answer(f"{text}\nВаш id: {user.get("cms_id")}")


async def main() -> None:
    scheduler = AsyncIOScheduler()

    scheduler.add_job(send_orders, 'interval', seconds=10)
    scheduler.start()

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
