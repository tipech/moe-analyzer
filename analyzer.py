"""Road network performance metrics calculation

This file contains classes used for calculation of several different road
network performance and traffic metrics from the Highway Capacity Manual.
(summary: https://ops.fhwa.dot.gov/publications/fhwahop08054/execsum.htm)

It can also be executed as a script, supplied with command line arguments.

Classes:
    MetricAnalyzer

"""

import xml.etree.ElementTree as ET
import argparse
from classes import Edge, Lane, Vehicle
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

        try:
            self.read_model(model)
            self.construct_systems()
            self.read_data(data)

        # I/O error checking
        except ET.ParseError as e:
            print("Problem while parsing xml file: ", e)
            exit()


    def read_model(self, file):
        """Parse a road network model from xml format to dictionary."""

        # xml file reading
        tree = ET.parse(file)
        root = tree.getroot()

        # model dictionary initialization
        self.model = {}

        # populate edges in road model
        for edge_xml in root.findall('edge'):

            # create edge object and store it keyed by id
            edge = Edge(edge_xml)
            self.model[edge.id] = edge


    def construct_systems(self):
        """Combine base items in road network to form larger-scale systems"""
        
        self.systems = {}

        # TODO later


    def read_data(self, file):
        """Parse traffic measurement data in Floating Car Data format."""

        # xml file reading
        tree = ET.parse(file)
        root = tree.getroot()

        self.vehicles = {}        # vehicle registry
        self.last_timestep = None # will remember previous time

        # iterate through timestops
        for time_xml in root.findall('timestep'):
            
            # iterate and read through vehicle measurements
            for vehicle_xml in time_xml.findall('vehicle'):
                self.read_vehicle_entry(vehicle_xml)

            self.compute_metrics(time_xml.attrib['time'])


    def read_vehicle_entry(self, vehicle_xml):
        """Read a single vehicle measurement entry and act accordingly"""

        # get vehicle id
        vehicle_id = vehicle_xml.attrib['id']

        # check if vehicle existed, if so update position
        if vehicle_id in self.vehicles:
            vehicle = self.vehicles[vehicle_id]
            vehicle.update(vehicle_xml)

            # existing vehicle changed edges within network
            if vehicle.changed and vehicle.edge in self.model:

                # update counters for new edge
                self.model[vehicle.edge].update_entered()

                # update counters for old edge
                self.model[vehicle.last_edge].update_left()

            # existing vehicle left network
            elif vehicle.changed and vehicle.edge not in self.model:

                # update counters for old edge
                self.model[vehicle.last_edge].update_left()

            # existing vehicle stayed in same edge
            elif not vehicle.changed and vehicle.edge in self.model:

                # update counters for old edge
                self.model[vehicle.last_edge].update_moved(vehicle)


        # this is a new vehicle, create object
        else:
            vehicle = Vehicle(vehicle_xml)

            # vehicle actually entered network, add to registry
            if vehicle.edge in self.model:
                self.vehicles[vehicle.id] = vehicle

                # update counters for new edge
                self.model[vehicle.edge].update_entered()


    def compute_metrics(self, timestep):
        """Compute and update metric values for one timestep."""

        timestep = float(timestep)

        # if it's not the very fist timestep, get time difference
        if self.last_timestep != None:
            time_diff = timestep - self.last_timestep

            # iterate through edges and compute metrics
            for edge in self.model.values():
                
                results = edge.compute_metrics(time_diff)

                if results[1] != 0:
                # if edge.id == "36921467":
                    print("Time:",timestep," Edge:",edge.id," Metrics:",results)



        # remember previous time
        self.last_timestep = timestep



if __name__ == "__main__":
    # Run the module with command-line parameters.
    main()

