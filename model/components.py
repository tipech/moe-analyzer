"""Road network model components

This file contains the classes used in the representation of the road network
model


Classes:
    System
    Junction
    Edge
    Lane
    Section

"""

import re
from pprint import pprint


class System():
    """Abstract representation of a system, to provide common methods"""
    def __init__(self):

        # setup vehicle counters
        self.v_current = 0 # vehicles in edge right now
        self.v_visited = 0 # total vehicles that passed through edge
        self.total_dist = 0 # total distance moved by vehicles in edge
        self.total_ideal_time = 0 # total free-flow time for same distance


    def compute_metrics(self, time_diff, min_speed):
        """Compute and update HCM MOE values for a generic system."""

        throughput = self.v_current / time_diff
        
        # if cars actually  passed
        if self.v_current != 0:

            # Total Delay calculation, min speed is 1 m/s to prevent artifacts
            total_time = time_diff * self.v_current
            total_delay = total_time - self.total_ideal_time

            # Percent Incomplete Trips, Delay per Trip, Travel Time Index
            pit = self.v_current / self.v_visited
            dpt = total_delay / self.v_current
            tti = total_time / self.total_ideal_time

        # no cars passed, default values
        else:

            total_delay = 0
            pit = 0 
            dpt = 0
            tti = 1

        return pit, throughput, total_delay, dpt, tti


class Junction():
    """Representation of a junction in a road network."""
    def __init__(self, junction):

        self.id = junction['id']
        self.internal_edges = {lane.rpartition('_')[0]
            for lane in junction['intLanes'].split()}

        self.assigned = False
        

    def get_neighbors(self, all_edges):
        """Retrieve the incoming and outgoing edges of a junction"""

        # get incoming and outgoing edges
        e_in = [e for e in all_edges.values() if e.to_id == self.id]
        e_out = [e for e in all_edges.values() if e.from_id == self.id]
        return e_in, e_out


    def __repr__(self):
        return ('{}({})'.format(self.__class__.__name__, self.id))


class Edge(System):
    """Representation of an edge in a road network."""
    def __init__(self, edge, lanes):
        super(Edge, self).__init__()

        self.id = edge['id']
        self.assigned = False

        # if normal function, store normal properties
        if 'function' not in edge or edge['function'] == "normal":

            self.function = "normal"            
            self.type = edge['type']
            self.from_id = edge['from']
            self.to_id = edge['to']

        # internal/junction edge, no properties
        else:
            self.function = edge['function']
            self.type = None
            self.from_id = None
            self.to_id = None

        # create lanes
        self.lanes =[Lane(self.id, lane) for lane in lanes]
        self.lane_count = len(self.lanes)

        # calculate edge min speed
        self.flow_speed = min([lane.speed for lane in self.lanes])


    def update_entered(self, distance):
        """Update edge vehicle counters when a vehicle just entered."""

        self.v_current += 1
        self.v_visited += 1
        self.total_dist += distance


    def update_moved(self, distance):
        """Update edge vehicle counters when a vehicle stayed in."""

        self.total_dist += distance


    def update_left(self):
        """Update edge vehicle counters when a vehicle just left."""

        self.v_current -= 1


    def compute_metrics(self, time_diff, min_speed):
        """Compute and update HCM MOE values for this edge."""

        # total distance, if cars almost stopped enforce speed 1 m/s per car
        self.total_dist = max(self.total_dist,
            self.v_current * min_speed * time_diff)
        self.total_ideal_time = self.total_dist / self.flow_speed
        
        return super(Edge, self).compute_metrics(time_diff, min_speed)


    def __repr__(self):
        return ('{}({})'.format(self.__class__.__name__, self.id))


class Lane():
    """Representation of a single lane of an edge in a road network."""
    def __init__(self, edge_id, lane):

        self.id = lane['id']
        self.edge = edge_id
        self.index = lane['index']
        self.speed = float(lane['speed'])
        self.length = float(lane['length'])
        # self.shape = lane['shape'].split(',')
        # self.disallow = lane['disallow'].split('_')

        
class Section(System):
    """Representation of a road segment or intersection."""
    def __init__(self, junction):
        super(Section, self).__init__()

        self.id = junction.id
        self.junctions = []
        self.edges = []
        self.exits = []


    def expand(self, junction, all_edges, all_junctions,
        greedy = False, first = True):
        """Recursively add edges to a section starting from a junction edge"""

        # save junction, find and save internal edges
        self.junctions.append(junction)
        junction.assigned = True
        for edge_id in junction.internal_edges:
            self.edges.append(all_edges[edge_id])
            all_edges[edge_id].assigned = True

        # get incoming and outgoing edges
        e_in, e_out = junction.get_neighbors(all_edges)

        # if it's the first call or the junction is an intersection
        if greedy or first or len(e_in) > 1 or len(e_out) > 1:

            # add incoming edges first
            for edge in e_in:
                if not edge.assigned and edge not in self.edges:

                    # add incoming edge to section and get its source
                    self.edges.append(edge)
                    edge.assigned = True
                    source = all_junctions[edge.from_id]                    
                    
                    # expand section from source
                    if not source.assigned and source not in self.junctions:
                        self.expand(source, all_edges, all_junctions,
                            greedy, False)

            # add outgoing edges next
            for edge in e_out:
                if not edge.assigned and edge not in self.edges:

                    # add outgoing edge to section and get its target
                    self.edges.append(edge)
                    edge.assigned = True
                    target = all_junctions[edge.to_id]
                    
                    # expand section from target,if it stopped this is an exit
                    if not target.assigned and target not in self.junctions:
                        if self.expand(target, all_edges, all_junctions,
                            greedy, False):
                            self.exits.append(edge)

            # this wasn't a final junction
            return False

        # if junction isn't intersection (stopping condition)
        else:
            return True


    def compute_metrics(self, time_diff, min_speed):
        """Compute and update HCM MOE values for this section"""

        # if sector contains edges
        if len(self.edges) > 0:

            # v_current is sum of vehicles currently in all edges
            self.v_current = sum([edge.v_current for edge in self.edges])

            # v_visited is sum of vehicles visited at the exits of section
            # or the current number of vehicles if no vehicles exited yet
            self.v_visited = max(sum([edge.v_visited for edge in self.exits]),
                max([edge.v_current for edge in self.edges]))

            # total ideal time is sum of times in all edges
            self.total_ideal_time = sum(
                [edge.total_ideal_time for edge in self.edges])

        # if section is isolated artifact without edges
        else:
            self.v_current = 0
            self.v_visited = 0
            self.total_ideal_time = 0

        return super(Section, self).compute_metrics(time_diff, min_speed)


    def __repr__(self):
        return ('{}({},Junctions:{},Edges:{})'.format(self.__class__.__name__,
            self.id, len(self.junctions), len(self.edges)))
        