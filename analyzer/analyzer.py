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
    def __init__(self, model, loader, calculation_rate = 2):

        # basic components and configuration properties
        self.model = model
        self.loader = loader
        self.calc_rate = calculation_rate # in seconds

        self.vehicles = {}      # vehicle registry
        self.last_cycle = 0     # processing cycle


    def get_next_metrics(self):
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
                metrics = self.compute_metrics(time_diff)

                # prepare for next cycle
                self.reset_counters()
                self.update_vehicles()
                self.last_cycle = self.last_cycle + self.calc_rate

                yield metrics, time


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

            if vehicle.new_entry is not None:

                # update counters for new edge
                if vehicle.new_entry.edge_id in self.model.edges:
                    (self.model.edge_systems[vehicle.new_entry.edge_id]
                        .update_entered(vehicle, time_diff))

                # update counters for new paths
                for system in self.model.path_systems.values():
                    if vehicle.new_entry.edge_id in system.edges:
                        system.update_entered(vehicle, time_diff)

                # update counters for new groups
                for system in self.model.custom_systems.values():
                    if vehicle.new_entry.edge_id in system.edges:
                        system.update_entered(vehicle, time_diff)


            if vehicle.last_entry is not None:

                # update counters for previous edge
                if vehicle.last_entry.edge_id in self.model.edges:
                    (self.model.edge_systems[vehicle.last_entry.edge_id]
                        .update_left(vehicle))

                # update counters for previous paths
                for system in self.model.path_systems.values():
                    if vehicle.last_entry.edge_id in system.edges:
                        system.update_left(vehicle)

                # update counters for previous groups
                for system in self.model.custom_systems.values():
                    if vehicle.last_entry.edge_id in system.edges:
                        system.update_left(vehicle)



    def compute_metrics(self, time_diff):
        """Execute the MOE computation for edges and sections."""

        # if it's not the very fist timestep
        if self.last_cycle != 0:


            # iterate through edges and compute metrics
            edge_metrics = {edge.id: edge.compute_metrics(time_diff)
                for edge in self.model.edge_systems.values()}
            
            # iterate through paths and compute metrics
            path_metrics = {path.id: path.compute_metrics(time_diff)
                for path in self.model.path_systems.values()}

            # iterate through paths and compute metrics
            group_metrics = {group.id: group.compute_metrics(time_diff)
                for group in self.model.custom_systems.values()}
            
            # return computed values
            return edge_metrics, path_metrics, group_metrics

        # if it's the first timestamp, return empty
        else:
            return {}, {}, {}


    def reset_counters(self):
        """Reset edge counters, prepare for next timestamp"""

        # loop through edges and set distance to 0
        for edge in self.model.edge_systems.values():
            edge.total_dist = 0


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