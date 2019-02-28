import pymongo, time
from model.network import RoadNetworkModel
from pprint import pprint



class MongoDBConnector:
	
	def __init__(self, url='mongodb://localhost:27017'):
		"""Initialize a single database session"""

		self.client = pymongo.MongoClient('mongodb://localhost:27017')
		self.db = self.client.traffic_performance
		self.network_collection = self.db["networks"]




	def store_execution(self, model, simulation):
		"""Store the road network info to the database."""

		# create a unique execution id
		execution_id = "%s_%s_%d" % (model.name, simulation,
			round(time.time()))

		# create an execution object
		try:
			result = self.network_collection.insert_one({
				'_id': execution_id,
				'network': model.name,
				'simulation': simulation})

		except pymongo.errors.DuplicateKeyError as e:
			print("Id already exists in the collection.")

		# create collections of edges for this execution
		self.edges_collection = self.db[execution_id + "_edges"]
		self.paths_collection = self.db[execution_id + "_paths"]
		self.groups_collection = self.db[execution_id + "_groups"]

		try:
			self.edges_collection.insert_many(
				{'_id': edge} for edge in model.edge_systems.keys())
			self.paths_collection.insert_many(
				{'_id': path} for path in model.path_systems.keys())
			self.groups_collection.insert_many(
				{'_id': path} for path in model.custom_systems.keys())

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


