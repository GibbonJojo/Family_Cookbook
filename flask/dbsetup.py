from pymongo import MongoClient
from SECRETS import *


def create_db():
    # connect to the client
    client = MongoClient(MDB_URI)

    # create and connect to the coobkook database
    db = client.cookbook

    # create the Users collection
    db_users = db.users

    # create the Recipe collection
    db_recipes = db.recipes

    # create the standard users
    create_users(db_users)


def create_user(db):
    jojo = {"username": "Gibbon",
            "password": "admin",
            "email": "johannes.uttecht@gmail.com",
            "settings": {},
            "status": {"admin": "True"}}

    insert_res = db.insert_one(jojo)
    print(insert_res.acknowledged)


if __name__ == "__main__":
    create_db()