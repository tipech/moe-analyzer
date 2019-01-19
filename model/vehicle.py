"""Incoming data loaders

This file contains loader classes that allow reading iteratively through
vehicle entry data for various different data formats


Classes:
    Vehicle
    Entry

"""


class Vehicle():
    """Representation of a single vehicle."""
    def __init__(self, entry):

        # vehicle properties
        self.id = entry.id
        self.type = entry.type

        self.last_entry = None
        self.new_entry = entry


    def update(self):
        """Shift new entries to last and prepare for new"""

        if self.new_entry != None:
            self.last_entry = self.new_entry
            self.new_entry = None


    def entered_network(self, network):
        """Check if vehicle just entered the road network."""
        return (self.last_entry is None
            or self.last_entry.edge_id not in network.edges)


    def left_network(self, network):
        """Check if vehicle just left the road network."""
        return (self.new_entry is None
            or self.new_entry.edge_id not in network.edges)


    def changed_edge(self):
        """Check if vehicle moved to a different edge in the road network."""
        return self.last_entry.edge_id != self.new_entry.edge_id


    def distance_moved(self):
        """Calculate the distance the vehicle traveled within the same edge"""
        return self.new_entry.pos - self.last_entry.pos


    def approx_distance_moved(self, time_diff):
        """Approximate the distance the vehicle traveled between edges"""
        return self.new_entry.speed * time_diff


    def __repr__(self):
        return ('{}({})'.format(self.__class__.__name__, self.id))



class Entry():
    """Representation of a single timestep sensor entry of a vehicle."""
    def __init__(self, entry, time):

        # vehicle properties
        self.id = entry['id']
        self.type = entry['type']
        self.time = time

        # extract edge and lane ids
        self.edge_id = entry['lane'].rpartition('_')[0]
        self.lane_id = entry['lane'].rpartition('_')[1]

        # store position in edge
        self.pos = float(entry['pos'])
        self.speed = float(entry['speed'])
        
        # store location/speed data
        # self.x = float(entry['x'])
        # self.y = float(entry['y'])


    def __repr__(self):
        return ('{}({})'.format(self.__class__.__name__, self.id))
        