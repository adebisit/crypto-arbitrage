from pymongo import MongoClient
from config import settings


client = MongoClient(settings.ATLAS_URI)
print(f'Connecting to Mongo DB Client {settings.ATLAS_URI}')
db = client[settings.DB_NAME]
print(f'Connecting to DB = {settings.DB_NAME}')