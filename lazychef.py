from __future__ import print_function
import web
import graphlab
import pymongo
import thread
import threading
import time
import os

CLIENT = None
RATINGS = None
RECOMMENDATIONS = None
LOCK = None
MONGO_HOME = '/Users/gicoviello/mongodb-osx-x86_64-2.4.9'

URLS = (
        '/recipes/(.*)', 'recipes',
        '/rating/(.*)/(.*)', 'rating'
)

class recipes:
	def GET(self, ingredients):

		ingredients = ingredients.split(',')
		recipe_has_ing = {}
		recipe_require_ing = {}
		recommandation = {}
		output = {}
		# For every ingredient user has, get all the recipes that uses the ingredient.
		#
		for ing in ingredients:
			rows = web.ctx.RECIPES.find({"ingredient":ing})
			print(rows.count())
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
					recipe_require_ing[key] = web.ctx.RECIPES.find({"recipe_name": key})
		# Update the ratingredients based on if an optional/required ing is present for each candidate recipe
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


class rating:
	def GET(self, user, recipe):
		rows = web.ctx.RATINGS.find({'user' : user, 'recipe' : recipe})
		if(rows.count() > 0):
			return rows[0]['rating']

		web.ctx.LOCK.acquire()
		rows = web.ctx.RECOMMENDATIONS.find({'user' : user, 'recipe' : recipe})
		rating = 3
		if(rows.count() > 0):
			rating = rows[0]['rating']
		web.ctx.LOCK.release()

		return rating

	def POST(self, user, recipe):
		web.ctx.RATINGS.insert({'user' : user, 'recipe' : recipe, 'rating' : int(web.data())})
		return 'OK'

def update_model():
	print("Updating model ....")
	os.system("%s/bin/mongoexport --host localhost --db lazychef --collection ratingredients -f user,recipe,rating --csv > ratingredients.csv" % MONGO_HOME)
	data = graphlab.SFrame.read_csv("ratingredients.csv", column_type_hints={"rating":int})
	model = graphlab.recommender.create(data, 'user', 'recipe', 'rating')
	LOCK.acquire()
	CLIENT.lazychef.recommendations.drop()
	RECOMMENDATIONS = CLIENT.lazychef.recommendations
	model.recommend(data).to_dataframe().apply(lambda row: RECOMMENDATIONS.insert({'user' : row['user'], 'recipe' : row['item'], 'rating' : row['score']}), axis=1)
	LOCK.release()

def model_updater():
	while True:
		update_model()
		time.sleep(60)

def ctx_processor(handler):
	web.ctx.RATINGS = RATINGS
	web.ctx.RECOMMENDATIONS = RECOMMENDATIONS
	web.ctx.RECIPES = RECIPES
	web.ctx.LOCK = LOCK
	return handler()

if __name__ == '__main__':
	CLIENT = pymongo.MongoClient()
	RATINGS = CLIENT.lazychef.ratings
	RECOMMENDATIONS = CLIENT.lazychef.recommendations
	RECIPES = CLIENT.lazychef.recipes
	LOCK = threading.Lock()
	update_model()
	thread.start_new_thread(model_updater, ())
	app = web.application(URLS, globals())
	app.add_processor(ctx_processor)
	app.run()
