from datetime import datetime

from bson import ObjectId
from bson.errors import InvalidId
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import users


class User:
    @staticmethod
    def create_user(name, email, password):
        user = {
            "name": name,
            "email": email,
            "password": generate_password_hash(password),
            "createdAt": datetime.utcnow(),
        }
        result = users.insert_one(user)
        user["_id"] = result.inserted_id
        return user

    @staticmethod
    def find_by_email(email):
        return users.find_one({"email": email})

    @staticmethod
    def find_by_id(user_id):
        try:
            return users.find_one({"_id": ObjectId(user_id)})
        except (InvalidId, TypeError):
            return None

    @staticmethod
    def verify_password(user, password):
        return check_password_hash(user["password"], password)
