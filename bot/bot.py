import asyncio
import base64
from datetime import datetime
from io import BytesIO

from aiogram import Dispatcher, Bot, types
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import CommandStart
from aiogram.types import Message, InputFile, BufferedInputFile
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from db import user_collection, order_collection

TOKEN = "7105828267:AAGlYANgVAHiUbDg2Zq7t6e2-5_MiEGIYB8"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot)


def order_to_text(order) -> str:
    order_text = f"<b>Заказ:</b>\n"
    order_text += f"<b>Название:</b> {order["name"]}\n"
    order_text += f"<b>Цена:</b> {order["price"]}\n"
    order_text += f"<b>Предоплата:</b> {order["prepayment"]}\n"
    order_text += f"<b>Состав:</b> {order["compound"]}\n"
    order_text += f"<b>Клиент:</b> {order["client"]}\n"
    order_text += f"<b>Доставка:</b> {order["delivery"]}\n"
    order_text += f"<b>Адрес:</b> {order["address"]}\n"
    order_text += f"<b>Комментарий:</b> {order["comment"]}\n"
    order_text += f"<b>Создан:</b> {order["created_at"]}\n"

    return order_text


async def send_orders():
    try:
        orders = await order_collection.find({}).to_list(None)
        for order in orders:
            order_text = order_to_text(order)

            image_base64 = order["image"]
            image_bytes = base64.b64decode(image_base64)
            for user in await user_collection.find({}).to_list(None):
                chat_id = user["chat_id"]
                try:
                    await bot.send_photo(chat_id, photo=BufferedInputFile(file=image_bytes, filename="gfdgdf"), caption=order_text, parse_mode='HTML')
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

    scheduler.add_job(send_orders, 'interval', seconds=10)
    scheduler.start()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
