import pymongo
from pymongo import MongoClient

class MongoDBConnector:
	
	def __init__(self, sections):
		self.client = MongoClient('mongodb://localhost:27017')
		self.db = self.client.traffic_performance
		self.tp_collection = self.db.traffic_performance

		try:
			result = self.tp_collection.insert_many({'_id' : id} for id in sections)
			print('Many posts: {0}'.format(result.inserted_ids))
		except pymongo.errors.BulkWriteError:
			print("Ids already exist in the collection.")

	def insert(self, results, timestep, edge):
		result = self.tp_collection.update_one(
			{'_id' : edge.id}, {"$push" : {'entries' : {'time' : timestep, 'pit' : results[0], 'throughput' : results[1], 'total_delay' : results[2], 'dpt' : results[3], 'tti' : results[4]}}}
		)
		
		# DEBUG
		print('One post: {0}'.format(edge.id))
