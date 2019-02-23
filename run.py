from analyzer.loaders import XmlDataLoader
from analyzer.analyzer import MOEAnalyzer
from database.db_connector import MongoDBConnector
from model.network import RoadNetworkModel


model = RoadNetworkModel("samples/kennedy.net.xml")
db_connector = MongoDBConnector("mongodb://localhost:27017")

db_connector.store_model(model)


loader = XmlDataLoader("samples/kennedy-output.xml")

# analyzer = MOEAnalyzer(model, loader)  # run the analyzer
