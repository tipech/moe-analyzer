import pymongo
from pymongo import MongoClient
import os
from pprint import pprint

class MongoDBConnector:
	
	def __init__(self, edges, sections, filename):
		self.client = MongoClient('mongodb://localhost:27017')
		self.db = self.client.traffic_performance

		self.collection_name = os.path.basename(filename).split('.')[0]
		self.edge_collection_name = self.collection_name + "-edges"
		self.group_collection_name = self.collection_name + "-groups"
		self.edge_collection = self.db[self.edge_collection_name]
		self.group_collection = self.db[self.group_collection_name]

		try:
			result = self.group_collection.insert_many({'_id' : id} for id in sections)
			print('Many posts: {0}'.format(result.inserted_ids))
		except pymongo.errors.BulkWriteError:
			print("Ids already exist in the collection.")

		try:
			result = self.edge_collection.insert_many({'_id' : id} for id in edges)
			print('Many posts: {0}'.format(result.inserted_ids))
		except pymongo.errors.BulkWriteError:
			print("Ids already exist in the collection.")

	def insert(self, results, timestep, measurement, type):
		
		if type == "edge":
			result = self.edge_collection.update_one(
				{'_id' : measurement.id}, {"$push" : {'entries' : {'time' : timestep, 'pit' : results[0], 'throughput' : results[1], 'total_delay' : results[2], 'dpt' : results[3], 'tti' : results[4]}}}
			)
		elif type == "group":
			result = self.group_collection.update_one(
				{'_id' : measurement.id}, {"$push" : {'entries' : {'time' : timestep, 'pit' : results[0], 'throughput' : results[1], 'total_delay' : results[2], 'dpt' : results[3], 'tti' : results[4]}}}
			)

		# DEBUG
		# print('One post: {0}'.format(edge.id))
