import os

from pymongo import MongoClient


mongo_client = MongoClient(os.environ["MONGO_URI"])
mongo = mongo_client.get_default_database()
tasks = mongo.tasks
