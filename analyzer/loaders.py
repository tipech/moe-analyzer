"""Incoming data loaders

This file contains loader classes that allow reading iteratively through
vehicle entry data for various different data formats


Classes:
    XmlDataLoader

"""

import xml.etree.ElementTree as ET
from model.vehicle import Entry
from pprint import pprint


class XmlDataLoader():
    """Initialize data loading from an xml file and return an iterator."""
    def __init__(self, filename):

        # parse xml file iteratively and get root element
        self.file = open(filename)
        self.context = ET.iterparse(self.file,events=('start','end'))
        self.context = iter(self.context)
        _, self.root = self.context.__next__()


    
    def read(self):
        """Read all the entries in a single timestamp and clean buffer."""

        # iterate through xml elements
        for event, elem in self.context:
            
            try:
                # if reached end of timestep, init new vehicle list
                if event == "end" and elem.tag == 'timestep':
                    entries = []
                    time = float(elem.attrib['time'])

                    # iterate through vehicle entries and store them
                    for entry in elem:
                        entries.append(Entry(entry.attrib, time))

                    # cleanup already read xml and yield time and entries
                    self.root.clear()
                    yield time, entries

            # Read error checking
            except ET.ParseError as e:
                print("Problem while reading xml file.\n", e)

        # end of file, close it
        self.file.close()

