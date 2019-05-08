import sys, os, json
from flask import Flask, render_template, request

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from model.network import RoadNetworkModel
from analyzer.loaders import XmlDataLoader
from analyzer.analyzer import MOEAnalyzer
from database.db_connector import MongoDBConnector

from pprint import pprint

# os.chdir("..")
app = Flask(__name__)
model = None


@app.route('/')
@app.route('/config')
def config():
    """Show the road network configuration view."""

    # get available networks and simulations
    root, networks = list_files("../data/networks/")
    _, simulations = list_files("../data/simulations/")
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

    

    # check if a model actually exists
    global model
    if model is None:
        return config()

    # add new group to model
    group = request.get_json()
    model.add_custom_system(group['name'], group['edges'])

    # re-load model details, networks and simulations for display
    details, edges, paths, groups = load_model(model)
    root, networks = list_files("data/networks")
    _, simulations = list_files("data/simulations")

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
    """Show the resulting metrics view."""

    # get analysis parameters and existing simulations
    root, simulations = list_files("../data/simulations/")
    parameters = request.args
    
    # check if model and simulation actually exist
    global model

    # DEBUG
    # model = RoadNetworkModel("../data/networks/", "kennedy.net.xml", shortest_paths=True)
    
    if (model is None or 'simulation' not in parameters
        or parameters['simulation'] not in simulations):
        return config()


    # load data and run the MOE analyzer
    loader = XmlDataLoader(os.path.join(root, parameters['simulation']))
    analyzer = MOEAnalyzer(model, loader, float(parameters['obs_rate']))


    history = {0: {}, 1: {}, 2: {}}
    times = []

    # go through entire observation time, calculate metrics and store them
    for metrics, time in analyzer.get_next_metrics():

        # perform this for edges, paths and groups
        for i in [0, 1, 2]:
        
            # store system metric results keyed by system id then by metric
            for _id, values in metrics[i].items():
                
                # if adding this system for the first time, add metric lists
                if _id not in history[i]:
                    history[i][_id] = {}

                    # insert first values to each metric list
                    for metric, value in values.items():
                        history[i][_id][metric] = [{"y": value, "x": time}]

                # if system has been added
                else:
                    # append new values to each metric list
                    for metric, value in values.items():
                        history[i][_id][metric].append({"y":value,"x":time})

            # also keep track of time
            times.append(time)

    # serialize final metrics into JSON
    for i in [0, 1, 2]:
        for _id, values in history[i].items():
            history[i][_id] = json.dumps(values)


    # insert calculated metric values to db
    # self.db.insert(edge_metrics, path_metrics, group_metrics)

    # load model and metric details for display
    details, edges, paths, groups = load_model(model)
    metrics = {
        "pit": "Percent incomplete trips",
        "thr": "Throughput",
        "td": "Total Delay",
        "dpt": "Delay per trip",
        "tti": "Travel time index"}

    return render_template('metrics.html',
        metrics=metrics,
        edges=edges,
        paths=paths,
        groups=groups,
        edge_metrics=history[0],
        path_metrics=history[1],
        group_metrics=history[2],
        start_time=times[0],
        end_time=times[len(times)-1])


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
        new_shape = edge.shape.transform(model.convBoundary,
            model.origBoundary)

        # edge dtails
        edges_dict[edge.id] = {
            'id': edge.id,
            'order': edge.shape.get_center()[0],   # order by latitude
            'shape': str(new_shape),
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
            'name': path.name.replace("->", u"\u2192 "),
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
    app.run(host= '0.0.0.0')