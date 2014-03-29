from flask import *
import interface as iface

app = Flask(__name__)

@app.route('/')
def main():
	return render_template("index.html", ings=iface.get_ingredients_all())

if __name__ == "__main__":
	app.run(debug = True)

