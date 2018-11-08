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

        # calculate edge min speed
        self.flow_speed = min([lane.speed for lane in self.lanes])

        # setup vehicle counters
        self.vehicles_current = 0 # vehicles in edge right now
        self.vehicles_visited = 0 # total vehicles that passed through edge

        self.valid_vehicles = 0   # valid vehicles for distance calculation
        self.total_distance = 0 # total distance moved by vehicles in edge


    def update_entered(self):
        """Update edge vehicle counters when a vehicle just entered."""

        self.vehicles_current += 1
        self.vehicles_visited += 1


    def update_moved(self, vehicle):
        """Update edge vehicle counters when a vehicle stayed in."""

        # vehicle is valid for edge distance calculation this timestep
        self.valid_vehicles += 1
        self.total_distance += vehicle.distance


    def update_left(self):
        """Update edge vehicle counters when a vehicle just left."""

        self.vehicles_current -= 1


    def compute_metrics(self, time_diff):
        """Compute and update metric values for this edge."""

        # common variables
        v_start_exit = 0 # since our observation time is entire data
        v_start_stay = 0 # no vehicles start in (TODO implement obsrv. window)
        v_enter_exit = self.vehicles_visited - self.vehicles_current
        v_enter_stay = self.vehicles_current

        total_time = time_diff * self.valid_vehicles
        total_ideal_time = self.total_distance / self.flow_speed
        
        # Throughput calculation
        throughput = v_start_exit + v_start_stay + v_enter_stay + v_enter_exit

        # Total Delay calculation
        total_delay = total_time - total_ideal_time

        # if cars actually  passed
        if throughput != 0:

            # Percent Incomplete Trips calculation
            pit = ((v_start_exit + v_start_stay + v_enter_stay) /
                (v_start_exit + v_start_stay + v_enter_stay + v_enter_exit))

            # Delay per Trip calculation
            dpt = total_delay / throughput

        else: # no cars passed
            pit = 0 
            dpt = 0

        # if there were valid cars (that stayed in the same system)
        if total_ideal_time != 0:

            # Travel Time Index calculation
            tti = total_time / total_ideal_time

        else: # no valid cars
            tti = 1

        # reset timestamp distance variables
        self.valid_vehicles = 0
        self.total_distance = 0

        return pit, throughput, total_delay, dpt, tti



class Lane():
    """Representation of a single lane of an edge in a road network."""
    def __init__(self, edge_id, lane_xml):

        self.id = lane_xml.attrib['id']
        self.edge = edge_id
        self.index = lane_xml.attrib['index']
        self.speed = float(lane_xml.attrib['speed'])
        self.length = float(lane_xml.attrib['length'])
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

        # store position in edge
        self.pos = float(vehicle_xml.attrib['pos'])

        # can't calculate distance moved in first timestep
        self.distance = None
        
        # store location/speed data
        # self.x = float(vehicle_xml.attrib['x'])
        # self.y = float(vehicle_xml.attrib['y'])
        # self.speed = float(vehicle_xml.attrib['speed'])


    def update(self, vehicle_xml):
        """Update the vehicle's state with new data."""

        # remember last edge
        self.last_edge = self.edge

        # extract new edge and lane ids
        self.edge = vehicle_xml.attrib['lane'].rpartition('_')[0]
        self.lane = vehicle_xml.attrib['lane'].rpartition('_')[1]

        # check if changed edges
        self.changed = self.last_edge != self.edge

        # if vehicle remained in same edge, calculate distance moved
        if not self.changed:
            self.distance = float(vehicle_xml.attrib['pos']) - self.pos
        
        else:
            self.distance = None

        # update position in edge
        self.pos = float(vehicle_xml.attrib['pos'])

        # store location/speed data
        # self.x = float(vehicle_xml.attrib['x'])
        # self.y = float(vehicle_xml.attrib['y'])
        # self.speed = float(vehicle_xml.attrib['speed'])
        
        
        
