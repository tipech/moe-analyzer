import sys, os
from flask import Flask, render_template, request
from pprint import pprint

sys.path.insert(1, os.path.join(sys.path[0], '..'))
# from database.db_connector import MongoDBConnector
from model.network import RoadNetworkModel


# os.chdir("..")
app = Flask(__name__)
# db = MongoDBConnector("mongodb://localhost:27017")
model = None


@app.route('/')
@app.route('/config')
def config():
    """Show the road network configuration view."""

    # get available networks and simulations
    root, networks = list_files("data/networks")
    _, simulations = list_files("data/simulations")
    selection = request.args.get('network')
    shortest_paths = request.args.get('shortest_paths')
    
    # one of the valid networks was selected, load it
    global model
    if selection is not None and selection in networks:

        model = RoadNetworkModel(root, selection, shortest_paths=="true")
        details, edges, paths, groups = load_model(model)

    # otherwise load empty values
    else:
        model = None
        details = None
        edges = {}
        paths = {}
        groups = {}

    return render_template('config.html',
        networks=networks,
        shortest_paths=shortest_paths,
        simulations=simulations,
        details=details,
        edges=edges,
        paths=paths,
        groups=groups)


@app.route('/add_edge_group', methods=['POST'])
def add_edge_group():
    """Add a custom group to the road network model."""

    group = request.get_json()
    
    # get available networks and simulations
    root, networks = list_files("data/networks")
    _, simulations = list_files("data/simulations")

    # re-load model to add new groups
    global model
    if model is not None:
        model.add_custom_system(group['name'], group['edges'])
        details, edges, paths, groups = load_model(model)
    
    else:
        details = None
        edges = {}
        paths = {}

    return render_template('config.html',
        networks=networks,
        shortest_paths=model.shortest_paths,
        simulations=simulations,
        details=details,
        edges=edges,
        paths=paths,
        groups=groups)


@app.route('/metrics')
def metrics():
    """Show the road network configuration view."""

    global model

    return render_template('metrics.html',
        edges=model.edge_systems,
        paths=model.path_systems,
        groups=model.custom_systems)


def list_files(path=""):
    """Find all road network files in the appropriate folder"""

    # look in the details working directory's subfolders
    if os.path.isdir(path):
        (root, _, filenames) = next(os.walk(path))
        return root, filenames

    # look in the subfolders of other same-level directories
    else:
        parent_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
        new_path = os.path.abspath(os.path.join(parent_dir, path))

        if os.path.isdir(new_path):
            (root, _, filenames) = next(os.walk(new_path))
            return root, filenames

        else:
            pass # TODO throw exception here


def load_model(model):
    """Handle necessary actions for model loading"""

    # load all edges in the network
    edges_dict = {}
    for edge in model.edges.values():

        # project edge shapes to original lat/lng coordinates
        edge.shape.transform(model.convBoundary, model.origBoundary)

        # edge dtails
        edges_dict[edge.id] = {
            'id': edge.id,
            'order': edge.shape.get_center()[0],   # order by latitude
            'shape': str(edge.shape),
            'type': edge.type,
            'lanes': len(edge.lanes),
            'speed': round(edge.flow_speed * 3.6),
            'length': edge.length
        }

    # sort edges by the order provided, get as list of tuples
    edges = sorted(edges_dict.items(), key=lambda x: x[1]['order'])

    # load all path systems in the network
    paths_dict = {}
    for path in model.path_systems.values():
        
        # path details
        paths_dict[path.id] = {
            'name': path.name,
            'order': path.name,  # order by name
            'length': round(sum(system.edge.length
                for system in path.edge_systems.values()),1),
            'edges': ','.join(str(system.edge.id)
                for system in path.edge_systems.values())
        }

    # sort paths by the order provided, get as list of tuples
    paths = sorted(paths_dict.items(), key=lambda x: x[1]['order'])

    # load all custom group systems in the network
    groups_dict = {}
    for group in model.custom_systems.values():
        
        # group details
        groups_dict[group.id] = {
            'name': group.name,
            'order': group.name,  # order by name
            'length': round(sum(system.edge.length
                for system in path.edge_systems.values()),1),
            'edges': ','.join(str(system.edge.id)
                for system in group.edge_systems.values())
        }

    # sort paths by the order provided, get as list of tuples
    groups = sorted(groups_dict.items(), key=lambda x: x[1]['order'])

    # general model details
    details = {
        'id': model.name,
        'edge_count': len(model.edges),
        'junction_count': len(model.junctions),
        'path_count': len(model.path_systems),
        'total_length': round(sum(edge.length
            for edge in model.edges.values()))/1000}

    return details, edges, paths, groups


if __name__ == "__main__":
    app.run()