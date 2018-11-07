"""Traffic metrics calculation

This script calculates several different metrics from the HCM

"""

import xml.etree.ElementTree as ET
import argparse
from pprint import pprint



def main():
    """Run the analyzer with command-line parameters."""

    # parser for command line arguments
    parser = argparse.ArgumentParser(
        description="Calculate traffic metrics.")

    # DEBUG: disabled normal execution
    # road model and data input arguments
    # parser.add_argument("model", help="road network model")
    # parser.add_argument("data", help="traffic data")

    # optional arguments: print/store results 
    # parser.add_argument("-p", "--print", action="store_true",
    #     help="print results to console")
    # parser.add_argument("-s", "--store", action="store_true",
    #     help="store results to file")
    
    args = parser.parse_args()              # parse the arguments


    # DEBUG: hardcoded inputs, always print results
    args.model = "kennedy.net.xml"
    args.data = "kennedy-output.xml"
    args.print = True


    analyzer = MetricAnalyzer(args.model, args.data)  # run the analyzer


    # print analyzer
    # if args.print:
    #     print(analyzer)




class MetricAnalyzer():
    """Class responsible for the metric calculation"""
    def __init__(self, model, data):

        self.read_model(model)
        self.construct_systems()
        self.read_data(data)



    def read_model(self, file):
        """Parse a road network model from xml format to dictionary."""
        
        try:

            # xml file reading
            tree = ET.parse(file)
            root = tree.getroot()

            # model dictionary initialization
            self.model = {}

            # populate edges in road model
            # store edge properties, lanes and initialize metrics
            for edge in root.findall('edge'):
                self.model[edge.attrib['id']] = {
                    'properties': edge.attrib,
                    'lanes': [lane.attrib['id']:lane.attrib
                        for lane in edge.findall('lane')]
                    'vehicles': {
                        'inside': 0,
                        'visited': 0
                        }
                    }

        # I/O error checking
        except ET.ParseError as e:
            print("There was a problem while parsing file: " + file, e)
            exit()


    def construct_systems(self):
        """Combine base items in road network to form larger-scale systems"""
        
        self.systems = {}

        # TODO later


    def read_data(self, file):
        """Parse traffic measurement data in Floating Car Data format."""

        try:

            # xml file reading
            tree = ET.parse(file)
            root = tree.getroot()

            # vehicle dictionary initialization
            self.vehicles = {}

            # iterate through timestops
            for time in root.findall('timestep'):
                
                # iterate through vehicle measurements
                for veh in time.findall('vehicle'):

                    veh_id = veh.attrib['id']
            
                    # if first time seeing vehicle, add to dictionary
                    if veh_id not in self.vehicles:
                        self.vehicles[veh_id] = {
                            'id': veh_id,
                            'properties': {'type': veh.attrib['type'] }
                        }

                    # if it's inside our model
                    if self.get_edge(veh.attrib['lane']) in self.model:

                        # if this vehicle was in the edge last time
                        if ('state' not in self.vehicles[veh_id] or 
                            self.vehicles[veh_id]['edge'] == ):





        # I/O error checking
        except ET.ParseError as e:
            print("There was a problem while parsing file: " + file, e)
            exit()


    def get_state_dict(self, vehicle):
        """Get the state of a single vehicle as a dictionary."""
        
        return {
            'edge': self.get_edge(vehicle['lane']),
            'lane': self.get_lane(vehicle['lane']),
            'pos': vehicle['pos'],
            'x': vehicle['x'],
            'y': vehicle['y'],
            'speed': vehicle['speed']
            }


    def get_edge(self, lane_id):
        """Get the id of the edge a lane belongs to."""
        
        return lane_id.rpartition('_')[0]


    def get_lane(self, lane_id):
        """Get the actual number of a lane."""
        
        return lane_id.rpartition('_')[2]





if __name__ == "__main__":
    # Run the module with command-line parameters.
    main()

