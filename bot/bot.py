import asyncio
import base64
from datetime import datetime
from io import BytesIO

from aiogram import Dispatcher, Bot, types
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import CommandStart
from aiogram.types import Message, InputFile, BufferedInputFile, InputMediaPhoto
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from db import user_collection, order_collection

# TOKEN = "6406386917:AAGdBAi0_FvUkpkuoyk9CJfC97ywNGfcVko"
TOKEN = "7105828267:AAGlYANgVAHiUbDg2Zq7t6e2-5_MiEGIYB8"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot)


def order_to_text(order) -> str:
    order_text = f"Заказ: \n"
    order_text += f"Название: {order["name"]}\n"
    order_text += f"Цена: {order["price"]}\n"
    order_text += f"Предоплата: {order["prepayment"]}\n"
    order_text += f"Состав: {order["compound"]}\n"
    order_text += f"Клиент: {order["client"]}\n"
    order_text += f"Доставка: {order["delivery"]}\n"
    order_text += f"Адрес: {order["address"]}\n"
    order_text += f"Комментарий: {order["comment"]}\n"
    order_text += f"Создан: {order["created_at"]}\n"

    return order_text


# async def send_orders():
#     try:
#         orders = await order_collection.find({}).to_list(None)
#         for order in orders:
#             order_text = order_to_text(order)
#
#             image_base64 = order["image"]
#             image_bytes = base64.b64decode(image_base64)
#             for user in await user_collection.find({}).to_list(None):
#                 chat_id = user["chat_id"]
#                 try:
#                     await bot.send_photo(chat_id, photo=BufferedInputFile(file=image_bytes, filename="gfdgdf"), caption=order_text, parse_mode='HTML')
#                 except TelegramAPIError as e:
#                     print(f"Failed to send message to chat_id {chat_id}: {e}")
#             await order_collection.delete_one({"_id": order["_id"]})
#     except Exception as e:
#         print(f"An error occurred while sending orders: {e}")

async def send_orders():
    try:
        orders = await order_collection.find({}).to_list(None)
        for order in orders:
            order_text = order_to_text(order)

            images_base64 = order.get("images", [])
            media_group = []
            for image_base64 in images_base64:
                image_bytes = base64.b64decode(image_base64)
                media_group.append(InputMediaPhoto(media=BufferedInputFile(file=image_bytes, filename="f"), caption=order_text[:1000]))
            for user in await user_collection.find({}).to_list(None):
                chat_id = user["chat_id"]
                try:
                    await bot.send_media_group(chat_id, media=media_group)
                    await bot.send_message(chat_id, order_text[:4000])
                except TelegramAPIError as e:
                    print(f"Failed to send message to chat_id {chat_id}: {e}")
            await order_collection.delete_one({"_id": order["_id"]})
    except Exception as e:
        print(f"An error occurred while sending orders: {e}")


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    user = await user_collection.find_one({"chat_id": message.from_user.id})
    if user is None:
        await user_collection.insert_one({"chat_id": message.from_user.id})
    await message.answer("Hello!")


async def main() -> None:
    scheduler = AsyncIOScheduler()

    scheduler.add_job(send_orders, 'interval', minutes=1)
    scheduler.start()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
