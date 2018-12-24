"""Road network performance analyzer components

This file contains classes that correspond to main components of the road
network performance analysis tool


Classes:
    XmlLoader

"""

import xml.etree.ElementTree as ET
import pprint


class XmlLoader():
    """A component used for loading Xml traffic data."""
    def __init__(self, filename):
        

