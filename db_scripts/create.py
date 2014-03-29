from pymongo import MongoClient

client = MongoClient()
db = client.recipes

db.posts.insert({"recipe_name": "pizza", "ingredient":"dough", "weight":5, "req": True, "url": "teste.com"})
print db.posts.find_one()

