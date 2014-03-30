from flask import *
import interface as iface
import sys
sys.path.append('../')
import query
import urllib2
import json

app = Flask(__name__)

@app.route('/')
def main():
	return render_template("index.html", ings=query.query_ings(query.set_up(client)))

@app.route('/_ings')
def ings():
	return jsonify(ings=query.query_ings(query.set_up(client)))

@app.route('/_cook')
def cook():
	"parsing arguments"
	ings_raw = request.args.get('ings', 0, type=str)
	# user_id = request.args.get('uid', 0, type=int)
	ings = ings_raw.split('_')
	"create response recipes"
	response = query.recommend_exact(query.collecting(query.set_up(client), ings))
	print 'response = ', response
	if response == []:
		recipes = links = scores = []
	else: 
		[recipes, links, scores] = zip(*response)
	return jsonify(recipes=recipes, links=links, scores=scores)

@app.route('/_cook_with_missing')
def cook_with_missing():
	"parsing arguments"
	ings_raw = request.args.get('ings', 0, type=str)
	ings = ings_raw.split('_')
	"create response recipes"
	response = query.recommend_with_missing(query.collecting(query.set_up(client), ings))
	print 'response = ', response
	if response == []:
		recipes = links = scores = []
	else: 
		[recipes, links, scores] = zip(*response)
	return jsonify(recipes=recipes, links=links, scores=scores)

@app.route('/_recipe_clean')
def recipe_clean():
	# strategy 1. readability.
	url = request.args.get('url', 0, type=str)
	# url = 'http://www.readability.com/api/content/v1/parser?url=%s&token=bce960b8684303b648a519238bb7f6ff3c1d1ddc'%url
	# response = json.load(urllib2.urlopen(url))

	# strategy 2. crawler. 
	response2 = query.page_info(url)

	#return jsonify(content=response[u'content'], image_url=response[u'lead_image_url'], ings=response2['ingredients']);
	# if(url.find('allrecipes') != -1) :
	# 	return jsonify(content=response[u'content'], image_url=response[u'lead_image_url'], ings=response2['ingredients']);
	# else:
	# print response2['image']
	return jsonify(content=response2['description'], image_url=response2['image'], ings=response2['ingredients']);
	
if __name__ == "__main__":
	client = query.connect()
	app.run(debug = True)
	client.close()

