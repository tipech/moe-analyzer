"""Road network model

This file contains the main road network model class


Classes:
    RoadNetworkModel

"""

import xml.etree.ElementTree as ET
import networkx as nx
import re

from model.base_components import *
from model.system_components import *
from pprint import pprint


class RoadNetworkModel():
    """Read an xml file and construct a representation of the road network"""
    def __init__(self, filename):

        # initialize components and parse file
        self.junctions = {}
        self.edges = {}
        self.edge_systems = {}
        self.bounds = {}
        self.graph = {}
        self.path_systems = {}
        self.custom_systems = {}

        # read low-level edges
        self.read_model(filename)

        # represent as directed graph
        self.construct_graph()

        # get graph entrances/exits (not of these types) and paths btw. them
        paths = self.get_paths(self.graph,
            {'highway.residential', 'highway.service'})

        self.path_systems = self.get_path_systems(paths)

        #create a MongoDB collection and store the edges by id
        # self.db = MongoDBConnector(self.sections)


    def read_model(self, filename):
        """Parse a road network model from xml format to dictionary."""

        # parse file
        root = ET.parse(filename).getroot()
        
        # iterate over network edges
        for edge_xml in root.findall('edge'):

            # create edge and edge system objects store, them keyed by id
            lanes = [lane_xml.attrib for lane_xml in edge_xml.findall('lane')]
            edge = Edge(edge_xml.attrib, lanes)
            self.edges[edge.id] = edge
            self.edge_systems[edge.id] = EdgeSystem(edge)


        # iterate over network junctions
        for junction_xml in root.findall('junction'):

            # create junction objects and store keyed by id (when possible)
            if junction_xml.attrib['type'] != "internal":
                junction = Junction(junction_xml.attrib)
                self.junctions[junction.id] = junction


        # get coordinate bounding box from edge shapes
        coords = list(zip(*[pair for edge in self.edges.values()
            for pair in edge.shape.points]))
        self.bounds = {'x0': min(coords[0]), 'y0': min(coords[1]),
            'x1': max(coords[0]), 'y1': max(coords[1])}

        # calculate aspect ratio 
        self.aspect_ratio = ((self.bounds['x1'] - self.bounds['x0'])
            / (self.bounds['y1'] - self.bounds['y0']))
        

    def construct_graph(self):
        """Create a directed graph representation fo the system."""

        self.graph = nx.DiGraph([(edge.from_id, edge.to_id, {'edge': edge})
            for edge in self.edges.values()])


    def get_paths(self, G, excluded_types={}):
        """Get all simple paths from entrances to exits of a given graph."""

        all_entrances = {node for node, in_degree in self.graph.in_degree()
            if in_degree == 0}
        all_exits = {node for node, out_degree in self.graph.out_degree()
            if out_degree == 0}

        # Nodes of certain types are not allowed to be entraces or exits, so
        # we determine the type of the junction based on its edges and then
        # we discard node if it's only connected to edges with excluded types
        filtered_entrances = {node for node in all_entrances 
            if not ({edge[2]['edge'].type
                for edge in self.graph.out_edges(node,True)} # edge types
                .issubset(excluded_types))}    # only connected to excl. types 

        # we repeat the same provess for exits
        filtered_exits = {node for node in all_exits 
            if not ({edge[2]['edge'].type
                for edge in self.graph.in_edges(node,True)}  # edge types
                .issubset(excluded_types))}    # only connected to excl. types

        # get all combinations of entrances and exits
        routes = ((source, target) for source in filtered_entrances
            for target in filtered_exits)
            
        # get all simple paths, groupped by route, as sequences of nodes
        pathlist = (nx.all_simple_paths(G, source, target)
            for (source, target) in routes)
        
        # flatten list and key paths by source-target pair 
        # (for paths with same source and target, also use incremental id)
        paths = {}
        for route in pathlist:
            for index, path in enumerate(route):

                # get first and last edge in path
                source = self.graph.get_edge_data(path[0], path[1])['edge'].id
                target = self.graph.get_edge_data(
                    path[len(path)-2], path[len(path)-1])['edge'].id

                paths[source + "->" + target + "|" + str(index)] = path


        # return flattenned list of paths, no longer groupped by route
        return paths

        
    def get_path_systems(self, paths):
        """Construct path system objects based on a set of paths."""

        path_systems = {}

        # for each path, get both normal and internal edges
        for path_id, path in paths.items():
            
            # get internal edges in each junction, flatten list
            junctions = (self.junctions[node] for node in path)
            internal_edges = {edge for junction in junctions
                for edge in junction.internal_edges}

            # get path as sequence of edges, make edge tuples to Edge objects
            normal_edges = [self.graph.get_edge_data(u,v)['edge'].id
                for u,v in nx.utils.pairwise(path)]

            # get ids of all normal and internal edges actually in the graph 
            valid_edges = set(self.edges).intersection(
                internal_edges.union(normal_edges))
            
            # create PathSystem object and add it to the list
            path_systems[path_id] = (PathSystem( path_id,
                (self.edge_systems[edge_id] for edge_id in valid_edges)))

        return path_systems


    def add_custom_system(self, name, edges):
        """Add a user-created multi-edge system to the model."""

        # create system, assign incremental id based on custom systems count
        system = CustomSystem( len(self.custom_systems),
                (self.edge_systems[edge_id] for edge_id in edges), name)

        self.custom_systems[system.id] = system