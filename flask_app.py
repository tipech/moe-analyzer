from flask import Flask
from flask import render_template
from flask import request
from pymongo import MongoClient
import json
from bson import json_util
from bson.json_util import dumps

client = MongoClient('mongodb://localhost:27017')
db = client['traffic_performance']

app = Flask(__name__)

@app.route("/")
def index():
	return render_template("index.html")

@app.route("/<path:collection>/edges")
def edges(collection):
	#collection = collection.split('=')[1]
	edge_collection_name = collection + "-edges"
	group_collection_name = collection + "-groups"
	edges = db[edge_collection_name].find({}, projection='_id')
	groups = db[group_collection_name].find({}, projection='_id')
	client.close()
	return render_template("edges.html", edges=edges, groups=groups, collection=collection)

@app.route("/<path:collection>/edge_id=<path:edge_id>&group_id=<path:group_id>")
def visualize_metrics(edge_id, group_id, collection):
	print(edge_id)
	print(group_id)

	if (edge_id != "0"):
		collection_name = collection + "-edges"
		current_id = edge_id
	else:
		collection_name = collection + "-groups"
		current_id = group_id

	print(collection)
	print(current_id)
	return render_template("metrics.html", edge_id=current_id, collection=collection_name)


@app.route("/edge/id=<path:edge_id>/collection=<path:collection>")
def calculate_metrics(edge_id, collection):
	#print(collection)
	#print(edge_id)
	projects = db[collection].find({ '_id' : edge_id })
	#376316643
	json_projects = []
	for project in projects:
		json_projects.append(project)
	json_projects = json.dumps(json_projects, default=json_util.default)
	client.close()
	return json_projects


if __name__ == "__main__":
	app.run(host='0.0.0.0',port=5000,debug=True)