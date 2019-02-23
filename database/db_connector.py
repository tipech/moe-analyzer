import pymongo
from model.network import RoadNetworkModel
from pprint import pprint



class MongoDBConnector:
	
	def __init__(self, url='mongodb://localhost:27017'):
		"""Initialize a single database session"""

		self.client = pymongo.MongoClient('mongodb://localhost:27017')
		self.db = self.client.traffic_performance
		self.network_collection = self.db["networks"]




	def store_model(self, model, network_id="kennedy"):
		"""Store the road network info to the database."""

		try:
			result = self.network_collection.insert_one({
				'_id': network_id,
				'bounds': model.bounds,
				'transform': model.transform})
			# print('Many posts: {0}'.format(result.inserted_ids))

		except pymongo.errors.DuplicateKeyError as e:
			print("Id already exists in the collection.")


		self.edge_collection = self.db[str(network_id) + "_edges"]
		self.sector_collection = self.db[str(network_id) + "_sectors"]

		edges = model.edges

		try:
			result = self.edge_collection.insert_many(
				{'_id': edge_id, 'shape': edge.shape}
				for edge_id, edge in edges.items())
			print('Many posts: {0}'.format(result.inserted_ids))

		except pymongo.errors.BulkWriteError as e:
			print("Ids already exist in the collection.")


	def get_networks(self):
		"""Retrieve a list of all stored road networks in the database."""

		return self.network_collection.find()


	def get_edges(self, network_id):
		"""Retrieve the edges of the stored road network from the database."""
		
		edge_collection = self.db[str(network_id) + "_edges"]
		return edge_collection.find()


	def insert_data(self, results, timestep, edge):
		result = self.tp_collection.update_one(
			{'_id' : edge.id}, {"$push" : {'entries' : {'time' : timestep, 'pit' : results[0], 'throughput' : results[1], 'total_delay' : results[2], 'dpt' : results[3], 'tti' : results[4]}}}
		)
		
		# DEBUG
		print('One post: {0}'.format(edge.id))


