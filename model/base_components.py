import re

class Junction():
    """Representation of a junction in a road network."""
    def __init__(self, junction):

        self.id = re.sub(r':?([^_]+).*', r'\1', junction['id'])
        self.internal_edges = {lane.rpartition('_')[0]
            for lane in junction['intLanes'].split()}

    def __repr__(self):
        return ('{}({})'.format(self.__class__.__name__, self.id))


class Edge():
    """Representation of an edge in a road network."""
    def __init__(self, edge, lanes):

        self.id = edge['id']

        # if normal function, store normal properties
        if 'function' not in edge or edge['function'] == "normal":

            self.function = "normal"            
            self.type = edge['type']
            self.from_id = edge['from']
            self.to_id = edge['to']

        # internal/junction edge, no properties
        else:
            self.function = edge['function']
            self.type = "internal"
            self.from_id = None
            self.to_id = None

        # get lanes and shape
        self.lanes =[Lane(self.id, lane) for lane in lanes]
        self.lane_count = len(self.lanes)
        self.shape = self.lanes[0].shape
        self.length = self.lanes[0].length

        # calculate edge min speed
        self.flow_speed = min([lane.speed for lane in self.lanes])


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
        self.shape = Shape(lane['shape'])
        # self.disallow = lane['disallow'].split('_')


class Shape():
    """Representation of the linear shape of a lane"""

    def __init__(self, serialized):
        """Deserialize a shape string into coordinate pairs"""
        coord_pairs = [pair.split(',') for pair in serialized.split(' ')]
        self.points = [(float(x), float(y)) for x, y in tuple(coord_pairs)]


    def transform(self, old, new):
        """Transform the shape points from one rectangle space to another."""

        for index, (x, y) in enumerate(self.points):

            new_x = (((x - old['x0']) / (old['x1'] - old['x0']))
                * (new['x1'] - new['x0']) + new['x0'])
            new_y = (((y - old['y0']) / (old['y1'] - old['y0']))
                * (new['y1'] - new['y0']) + new['y0'])

            self.points[index] = (new_x, new_y)


    def get_center(self, rounded=False):
        """Calculate and return the center point of this lane."""

        x, y = zip(*[pair for pair in self.points])
        
        if rounded:
            return round(sum(x)/len(x)), round(sum(y) / len(y))
        else:
            return sum(x)/len(x), sum(y) / len(y)


    def __str__(self):
        """Serialize and return a shape string from the coordinate pairs"""
        coord_pairs = [str(x) + ',' + str(y) for x, y in self.points]
        return ' '.join(coord_pairs)