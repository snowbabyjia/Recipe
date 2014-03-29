from flask import *
import interface as iface
import sys
sys.path.append('../')
import query

app = Flask(__name__)

@app.route('/')
def main():
	print query.query_ings(query.set_up(client))
	return render_template("index.html", ings=query.query_ings(query.set_up(client)))

@app.route('/_cook')
def cook():
	"parsing arguments"
	ings_raw = request.args.get('ings', 0, type=str)
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
if __name__ == "__main__":
	client = query.connect()
	app.run(debug = True)
	client.close()

