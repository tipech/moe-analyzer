
from model.network import RoadNetworkModel
from dataio.loaders import XmlDataLoader
from analyzer.analyzer import MOEAnalyzer



model = RoadNetworkModel("samples/kennedy.net.xml")
loader = XmlDataLoader("samples/kennedy-output.xml")

analyzer = MOEAnalyzer(model, loader)  # run the analyzer
