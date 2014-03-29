from pymongo import MongoClient
import sys

client = MongoClient()
db = client.recipes

def find_url(recipe_name):
    return str( db.posts.find_one({"recipe_name": recipe_name})["url"])

def add_data( file_name):
    data_file = open(file_name, "r")
    for line in data_file:
    
        if line[0] != '#':
            
            data = {}
            values = line.split('|')
            for i in range(len(values)):
                values[i] = values[i].strip()

            data["recipe_name"] = values[0]
            data["ingredient"] = values[1]
            data["weight"] = float(values[2])
            if values[3] == "True":
                data["req"] = True
            elif values[3] == "False":
                data["req"] = False
                
            data["rating"] = float(values[4])
            data["url"] = values[5]

            if not db.posts.find_one(data):
                db.posts.insert(data)


    
