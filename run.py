
from model.network import RoadNetworkModel
from dataio.loaders import XmlDataLoader
from analyzer.analyzer import MOEAnalyzer
import sys, os

if len(sys.argv) < 3:
	print("Please input the road network and simulation output files as arguments when running the program.")

elif not (os.path.exists(sys.argv[1]) or os.path.exists(sys.argv[2])):
	print("Files do not exist.")

else:
	model = RoadNetworkModel(sys.argv[1])
	loader = XmlDataLoader(sys.argv[2])

	analyzer = MOEAnalyzer(model, loader)  # run the analyzer
