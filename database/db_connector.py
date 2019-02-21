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
		# DEBUG
		#self.static_visual(60, 50, 300)
		
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

	def static_visual(self, rate, start, stop):

		# The pipeline gets all documents in a collection,
		# filters out entries not within start and stop,
		# groups and sorts them by time of "rate" increments,
		# and returns the documents grouped by edge/collection id (i.e., in its original form)

		pipeline = [
			{"$unwind": "$entries"},
			{
				"$match": {
					"entries.time": {
						"$gte": start,
						"$lte": stop
					}
				}
			}, {
				"$addFields": {
					"slot": {
						"$multiply": [{"$ceil": {"$divide": ["$entries.time", rate]}}, rate]
					}
				}
			}, {
				"$group": {
					"_id": {
						"_id": "$_id",
						"time": "$slot"
					},
					"avg_pit": {
						"$avg": "$entries.pit"
					},
					"avg_throughput": {
						"$avg": "$entries.throughput"
					},
					"avg_total_delay": {
						"$avg": "$entries.total_delay"
					},
					"avg_dpt": {
						"$avg": "$entries.dpt"
					},
					"avg_tti": {
						"$avg": "$entries.tti"
					}
				}
			}, {
				"$sort": {
					"_id.time": 1
				}
			}, {
				"$group": {
					"_id": "$_id._id",
					"entries": {
						"$push": {
							"time": "$_id.time",
							"avg_pit": "$avg_pit",
							"avg_throughput": "$avg_throughput",
							"avg_total_delay": "$avg_total_delay",
							"avg_dpt": "$avg_dpt",
							"avg_tti": "$avg_tti"
						}
					}
				}
			}
		]

		pprint(list(self.group_collection.aggregate(pipeline)))
