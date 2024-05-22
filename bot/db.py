from motor import motor_asyncio

MONGO_DETAILS = "mongodb://mongo:27017/bot"
# MONGO_DETAILS = "mongodb://localhost:27017"

client = motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

database = client.bot

user_collection = database.get_collection("users_collection")
order_collection = database.get_collection("order_collection")