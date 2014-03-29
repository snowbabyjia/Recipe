from flask import *
import interface as iface
import sys
sys.path.append('../')
import query

app = Flask(__name__)

@app.route('/')
def main():
	return render_template("index.html", ings=iface.get_ingredients_all())

@app.route('/_cook')
def cook():
	"parsing arguments"
	ings_raw = request.args.get('ings', 0, type=str)
	ings = ings_raw.split('_')
	"create response recipes"
	response = query.query(query.set_up(client), ings)
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

