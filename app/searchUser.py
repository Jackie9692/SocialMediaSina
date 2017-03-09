# -*- coding: utf-8 -*-

import sys
from flask import Flask, render_template, request, json
from elasticsearch import Elasticsearch

reload(sys)  
sys.setdefaultencoding('utf8')

es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

itemsPerPage = 50

def searchUser(request):
	#name
	user_id = request.args.get('user_id')
	if user_id != None:
		res = es.search(index="raw_data_db", doc_type='user_account_common,user_account_follows',
			body={
				"query": {
					"bool": {
						"filter": {"match_phrase": {"user_id": user_id}}
					},
				},
			})
		
		print res['hits']['total']
		return json.dumps(res['hits']['hits'][0]['_source'])
	return "Error 404"

def searchUserList(request):
	#search
	filter = []

	#name
	name = request.args.get('name')
	if name != None and name != "":
		for word in name.split():
			filter.append({"bool": {"should": [
				{"match_phrase": {"name": word}}, 
				{"match_phrase": {"screen_name": word}}
			]}})

	#location
	location = request.args.get('location')
	if location != None and location != "":
		for word in location.split():
			filter.append({"match_phrase": {"location": word}})

	#followers
	followers = request.args.get('followers')
	if followers != None and followers != 0:
		greaterThan = request.args.get('greaterThan')
		if greaterThan == None or greaterThan == 'true':
			filter.append({"range": {"followers_count": {"gt": followers}}})
		elif greaterThan == 'false':
			filter.append({"range": {"followers_count": {"lt": followers}}})

	#rate
	rate = request.args.get('rate')
	if rate != None:
		rate = json.loads(rate)
		if not 'minValue' in rate:
			pass
		elif not 'maxValue' in rate:
			pass
		elif rate['minValue'] != 0 and rate['maxValue'] != 100:
			filter.append({"range": {"rate": {"gte": rate['minValue'], "lte": rate['maxValue']}}})

	#category
	category = request.args.get('category')
	if category != None:
		category = json.loads(category)
		allTrue = True
		allFalse = True

		for item in category:
			allTrue = allTrue and category[item]
			allFalse = allFalse and not category[item]

		if not allTrue and not category:
			categoryFilter = []
			for item in category:
				if feelings[item]:
					categoryFilter.append({"match_phrase": {"category": item}})
			filter.append({"bool": {"should": categoryFilter}})

	#gender
	gender = request.args.get('gender')
	if gender != None and gender != "both":
		if gender == "male":
			filter.append({"match_phrase": {"gender": "m"}})
		if gender == "female":
			filter.append({"match_phrase": {"gender": "f"}})

	#orderBy
	sortBy = 'created_at'
	orderBy = request.args.get('orderBy')
	if orderBy == None:
		sortBy = 'created_at'
	elif orderBy == 'date':
		sortBy = 'created_at'
	elif orderBy == 'name':
		sortBy = 'name'

	orderMethod = 'desc'
	reverse = request.args.get('reverse')
	if reverse == None or reverse == 'true':
		orderMethod = 'asc'

	page = int(request.args.get('page')) * itemsPerPage

	res = es.search(index="raw_data_db", doc_type='user_account_common,user_account_follows', size=itemsPerPage, from_=page,
		body={
			"query": {
				"bool": {
					"filter": filter
				},
			},
			"highlight": {
				"pre_tags" : ["<em class='highlight'>"],
				"post_tags" : ["</em>"],
				"fields" : {
					"name" : {},
					"screen_name": {},
				}
			},
			"sort": {
				sortBy: {"order": orderMethod}
			}
		})

	print res['hits']['total']
	return json.dumps(res['hits'])