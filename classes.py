"""Road network classes

This file contains classes used by analyzer.py

"""

import pprint


class Edge():
    """Representation of an edge in a road network."""
    def __init__(self, edge_xml):

        self.id = edge_xml.attrib['id']

        # store edge function/type
        if 'function' in edge_xml.attrib: 
            self.type = edge_xml.attrib['function']
        elif 'type' in edge_xml.attrib: 
            self.type = edge_xml.attrib['type']
        else:
            self.type = "special"

        # create lanes
        self.lanes =[Lane(self.id, lane) for lane in edge_xml.findall('lane')]
        self.lane_count = len(self.lanes)

        # setup vehicle counters
        self.vehicles_current = 0 # vehicles in edge right now
        self.vehicles_visited = 0 # total vehicles that passed through edge

        # metrics variables


    def update_entered(self):
        """Update edge vehicle counters when a vehicle just entered."""

        self.vehicles_current += 1
        self.vehicles_visited += 1


    def update_left(self):
        """Update edge vehicle counters when a vehicle just left."""

        self.vehicles_current -= 1



class Lane():
    """Representation of a single lane of an edge in a road network."""
    def __init__(self, edge_id, lane_xml):

        self.id = lane_xml.attrib['id']
        self.edge = edge_id
        self.index = lane_xml.attrib['index']
        self.speed = lane_xml.attrib['speed']
        self.length = lane_xml.attrib['length']
        # self.shape = lane_xml.attrib['shape'].split(',')
        # self.disallow = lane_xml.attrib['disallow'].split('_')



class Vehicle():
    """Representation of a single vehicle."""
    def __init__(self, vehicle_xml):

        # vehicle properties
        self.id = vehicle_xml.attrib['id']
        self.type = vehicle_xml.attrib['type']

        # extract edge and lane ids
        self.edge = vehicle_xml.attrib['lane'].rpartition('_')[0]
        self.lane = vehicle_xml.attrib['lane'].rpartition('_')[1]

        # fresh object, changed edges
        self.last_edge = None
        self.changed = True

        # store location/trajectory data
        # self.pos = vehicle_xml.attrib['pos']
        # self.x = vehicle_xml.attrib['x']
        # self.y = vehicle_xml.attrib['y']
        # self.speed = vehicle_xml.attrib['speed']


    def update(self, vehicle_xml):
        """Update the vehicle's state with new data."""

        # remember last edge
        self.last_edge = self.edge

        # extract new edge and lane ids
        self.edge = vehicle_xml.attrib['lane'].rpartition('_')[0]
        self.lane = vehicle_xml.attrib['lane'].rpartition('_')[1]

        # check if changed edges
        self.changed = self.last_edge != self.edge

        # store location/trajectory data
        # self.pos = vehicle_xml.attrib['pos']
        # self.x = vehicle_xml.attrib['x']
        # self.y = vehicle_xml.attrib['y']
        # self.speed = vehicle_xml.attrib['speed']

        
        
        
