"""Road network model

This file contains the main road network model class


Classes:
    RoadNetworkModel

"""

import xml.etree.ElementTree as ET
import re
from model.components import *
from database.db_connector import MongoDBConnector

from pprint import pprint


class RoadNetworkModel():
    """Read an xml file and construct a representation of the road network"""
    def __init__(self, filename):

        # initialize components and parse file
        self.edges = {}
        self.junctions = {}

        # read low-level edges and construct larger systems
        self.read_model(filename)
        self.construct_sections()

        #create a MongoDB collection and store the edges by id
        self.db = MongoDBConnector(self.sections)

    def read_model(self, filename):
        """Parse a road network model from xml format to dictionary."""

        # parse file
        root = ET.parse(filename).getroot()
        
        # iterate over network edges
        for edge_xml in root.findall('edge'):

            # create lanes, edge objects and store edge keyed by id
            lanes = [lane_xml.attrib for lane_xml in edge_xml.findall('lane')]
            edge = Edge(edge_xml.attrib, lanes)
            self.edges[edge.id] = edge

        # iterate over network junctions
        for junction_xml in root.findall('junction'):

            # create junction objects and store keyed by id (when possible)
            if junction_xml.attrib['type'] != "internal":
                junction = Junction(junction_xml.attrib)
                self.junctions[junction.id] = junction


    def construct_sections(self):
        """Combine base road network edges to form mid-scale sections"""
        
        self.sections = {}
        remaining_junctions = dict(self.junctions)

        # iterate through intersection junctions (sorted for consistency)
        for junction in sorted(self.junctions.values(), key=lambda j: j.id):
            if not junction.assigned:

                # create new section object and get adjacent edges
                section = Section(junction)
                e_in, e_out = junction.get_neighbors(self.edges)

                # if junction is an intersection, expand and store it
                if len(e_in) > 1 or len(e_out) > 1:
                    section.expand(junction, self.edges, self.junctions)
                    self.sections[section.id] = section

        # iterate through the rest of the junctions (sorted for consistency)
        for junction in sorted(self.junctions.values(), key=lambda j: j.id):
            if not junction.assigned:

                # create new section object and expand it as necessary
                section = Section(junction)
                section.expand(junction, self.edges, self.junctions, True)
                self.sections[section.id] = section

        # iterate through remaining unassigned edges
        for edge in self.edges.values():
            if not edge.assigned:
                
                # if not an internal edge, get source junction
                if edge.function != "internal":
                    junction = self.junctions[edge.to_id]

                else:
                    junction = re.sub(r':?([^_]+).*', r'\1', edge.id)

                # add edge to junction's sector 
                for section in self.sections.values():
                    if junction in section.junctions:
                        section.edges.append(edge)



    # def construct_systems(self):
    #     """Combine road network sections to form large-scale systems"""
        
    #     self.systems = {}

    #     # TODO later
