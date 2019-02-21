"""Road network performance metrics calculation

This file contains classes used for calculation of several different road
network performance and traffic metrics from the Highway Capacity Manual.
(summary: https://ops.fhwa.dot.gov/publications/fhwahop08054/execsum.htm)

Classes:
    MOEAnalyzer

"""

from model.vehicle import Vehicle
from pprint import pprint



class MOEAnalyzer():
    """Class responsible for the metric calculation"""
    def __init__(self, model, loader, calculation_rate = 1, min_speed = 1):

        # basic components and configuration properties
        self.model = model
        self.loader = loader
        self.calc_rate = calculation_rate # in seconds
        self.min_speed = min_speed

        self.vehicles = {}      # vehicle registry
        self.last_cycle = 0     # processing cycle

        self.main_loop()


    def main_loop(self):
        """Loop through timesteps as provided from loader and calculate."""

        # time loop
        for time, entries in self.loader.read():

            # loop over vehicle entries in single timestamp and update values
            for entry in entries:
                self.read_entry(entry)

            # if elapsed time more that calculation period, time for new cycle
            time_diff = time - self.last_cycle
            if time_diff >= self.calc_rate:

                # update edges and calculate metrics for this cycle
                self.update_counters(time_diff)
                self.compute_metrics(time_diff)

                # prepare for next cycle
                self.reset_counters()
                self.update_vehicles()
                self.last_cycle = self.last_cycle + self.calc_rate


    def read_entry(self, entry):
        """Store or update a single vehicle entry and its last state."""

        # if vehicle is seen for the first time, create it
        if entry.id not in self.vehicles.keys():
            self.vehicles[entry.id] = Vehicle(entry)

        # if vehicle was already in system, update entry
        else:
            self.vehicles[entry.id].new_entry = entry


    def update_counters(self, time_diff):
        """Update vehicles and distance counters in the network"""

        for vehicle in self.vehicles.values():

            # if vehicle just entered the network
            if vehicle.entered_network(self.model):

                # update counters for new edge
                self.model.edges[vehicle.new_entry.edge_id].update_entered(
                    vehicle.approx_distance_moved(time_diff))

            # if existing vehicle just left the network
            elif vehicle.left_network(self.model):

                # update counters for old edge
                self.model.edges[vehicle.last_entry.edge_id].update_left()

            # if existing vehicle changed edges within network
            elif vehicle.changed_edge():

                # update counters for new edge
                self.model.edges[vehicle.new_entry.edge_id].update_entered(
                    vehicle.approx_distance_moved(time_diff))

                # update counters for old edge
                self.model.edges[vehicle.last_entry.edge_id].update_left()

            # if existing vehicle stayed in the same edge
            else:

                # update counters for old edge
                self.model.edges[vehicle.last_entry.edge_id].update_moved(
                    vehicle.distance_moved())


    def compute_metrics(self, time_diff):
        """Execute the MOE computation for edges and sections."""

        # if it's not the very fist timestep
        if self.last_cycle != 0:

            # iterate through edges and compute metrics
            for edge in self.model.edges.values():    
                results = edge.compute_metrics(time_diff, self.min_speed)
                self.model.db.insert(results, self.last_cycle, edge, type="edge")


            # iterate through sections and compute metrics
            for section in self.model.sections.values():    
                results = section.compute_metrics(time_diff, self.min_speed)

                # DEBUG
                #if section.id == "1367240508":
                    #print("Time:",self.last_cycle," Edge:",section.id," Metrics:",results)
                self.model.db.insert(results, self.last_cycle, section, type="group")


    def reset_counters(self):
        """Reset edge counters, prepare for next timestamp"""

        # loop through edges and set distance to 0
        for edge in self.model.edges.values():
            edge.total_dist = 0

            # NOTE: vehicle entry can be logged/backed up here if necessary


    def update_vehicles(self):
        """Cleanup vehicles not seen recently, prepare for new entries"""

        # loop through copy of list for safe deletion
        for v_id, vehicle in list(self.vehicles.items()):
            
            # if no new entries, delete
            if vehicle.new_entry is None:
                del self.vehicles[v_id]

            # otherwise mark new entries as last
            else:
                self.vehicles[v_id].update()

            # NOTE: vehicle entry can be logged/backed up here if necessary