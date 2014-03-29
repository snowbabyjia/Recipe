from pymongo import MongoClient
import sys

client = MongoClient()
db = client.recipes

def find_url(recipe_name):
    return str( db.posts.find_one({"recipe_name": recipe_name})["url"])
    
