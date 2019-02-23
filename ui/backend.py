import sys, os
from flask import Flask, render_template, request
from pprint import pprint

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from database.db_connector import MongoDBConnector
from model.network import RoadNetworkModel


os.chdir("..")
app = Flask(__name__)
db = MongoDBConnector("mongodb://localhost:27017")


@app.route('/')
@app.route('/config')
def index():
    """Show the configuration tab without loaded road networks."""

    networks = list_networks()
    simulations = list_simulations()
    selection = request.args.get('network')
    current = None
    map_width = 0
    map_height = 0
    edges_dict = {}
    
    if selection is not None and selection in networks:

        model = RoadNetworkModel("data/networks/" + selection)

        map_width = 800
        map_height = map_width / model.aspect_ratio
        map_bounds = {'x0': 0, 'x1': map_width, 'y0': 0, 'y1': map_height}

        for edge in model.edges.values():

            edge.shape.transform(model.bounds, map_bounds)

            edges_dict[edge.id] = {
                'id': edge.id,
                'order': edge.shape.get_center()[0],
                'shape': str(edge.shape),
                'type': edge.type,
                'lanes': len(edge.lanes),
                'speed': round(edge.flow_speed * 3.6),
                'length': edge.length
            }

        current = {
            'id': selection,
            'edge_count': len(model.edges),
            'junction_count': len(model.junctions),
            'total_length': round(sum(edge.length
                for edge in model.edges.values()))/1000,
            }


    return render_template('config.html',
        networks=networks,
        simulations=simulations,
        current=current,
        edges=sorted(edges_dict.items(), key=lambda x: x[1]['order']),
        map_width=map_width,
        map_height=map_height)



@app.route('/add_edge_group', methods=['POST'])
def add_edge_group():
    """Show the configuration tab without loaded road networks."""

    print(request.form['name'])
    return "OK"



def list_networks(path="data/networks"):
    """Finds all road network files in the appropriate folder"""

    (_, _, filenames) = next(os.walk(path))
    return filenames


def list_simulations(path="data/simulations"):
    """Finds all traffic simulation files in the appropriate folder"""

    (_, _, filenames) = next(os.walk(path))
    return filenames