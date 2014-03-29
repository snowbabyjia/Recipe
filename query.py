from pymongo import MongoClient

def connect():
	client = MongoClient()
	return client

def set_up(client):
	# db = client.db
	# db.recipe.drop()
	# recipe_collection = db.recipe
	# recipe_collection.insert({"recipe_name":"R1", "ingredient":"I1", "weight":1, "req":True, "rating": 100, "url":"www.google.com"})
	# recipe_collection.insert({"recipe_name":"R1", "ingredient":"I2", "weight":2, "req":False, "rating": 100, "url":"www.google.com"})
	# recipe_collection.insert({"recipe_name":"R2", "ingredient":"I1", "weight":2, "req":False, "rating": 20, "url":"www.facebook.com"})
	# recipe_collection.insert({"recipe_name":"R2", "ingredient":"I3", "weight":3, "req":True, "rating": 20, "url":"www.facebook.com"})
	# recipe_collection.insert({"recipe_name":"R2", "ingredient":"I4", "weight":4, "req":False, "rating": 20, "url":"www.facebook.com"})

	# return recipe_collection
	return client.recipes.posts

"FIXME: query and return all ingredients."
def query_ings(recipe_collection):
	# print recipe_collection.distinct("ingredient")
	return sorted(recipe_collection.distinct("ingredient"))
	

def query(recipe_collection, ings):
	recipe_has_ing = {}
	recipe_require_ing = {}
	recommandation = {}
	output = {}
	# For every ingredient user has, get all the recipes that uses the ingredient.
	# 
	for ing in ings:
		rows = recipe_collection.find({"ingredient":ing})
		#print rows.count()
		# For every row that the ingredient is in, put the ingredient in the recipe entry in recipe_list
		for i in range(rows.count()):
			row = rows[i]
			# key is the recipe_name
			key = row["recipe_name"]
			if not recipe_has_ing.has_key(key):
				recipe_has_ing[key] = []
			recipe_has_ing[key].append(ing)
			# Add this recipe to potential recommanded recipes. initial rating is 0
			if not recommandation.has_key(key):
				recommandation[key] = 0.0

			# Add the recipe and its required ingredients to the dict
			if not recipe_require_ing.has_key(key):
				# the value is a cursor object
				recipe_require_ing[key] = recipe_collection.find({"recipe_name": key})
	# Update the ratings based on if an optional/required ing is present for each candidate recipe
	for candidate in recommandation.keys():
		total_weight = 0 # this is the total weight of ingredients of this recipe. Used for normalize
		cursor = recipe_require_ing[candidate]
		candidate_rating = 0
		candidate_url = ""
		for i in range(cursor.count()):
			#each req_ing is a row in db that this candidate recipe is related
			req_ing = cursor[i]
			candidate_rating = req_ing["rating"]
			candidate_url = req_ing["url"]
			total_weight += req_ing["weight"]
			if req_ing["ingredient"] in recipe_has_ing[candidate]:
				recommandation[candidate] += req_ing["weight"]
			# if user does not have a required ing, delete this candidate.
			elif req_ing["req"]:
				del recommandation[candidate]
				break
			else:
				continue
		# If candidate is still in recommandation list, compute the rating
		if candidate in recommandation:
			recommandation[candidate] *= 1.0*candidate_rating/total_weight
			recommandation[candidate] = int(recommandation[candidate] * 100) / 100.0
			output[(candidate, candidate_url, recommandation[candidate])] = recommandation[candidate]

	# TODO: sort the recommandation
	return sorted(output, key=output.get, reverse=True)

if __name__ == "__main__":
	client = connect()
	print query_ings(set_up(client))
	ing = ["Yeast", "Water"]
	print query(set_up(client), ing)
	client.close()





