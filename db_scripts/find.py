from pymongo import MongoClient

client = MongoClient()
db = client.recipes

for post in db.posts.find():
    print post
