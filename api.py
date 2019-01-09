from flask import Flask, jsonify, request
from elasticsearch import Elasticsearch
from datetime import datetime

es = Elasticsearch() #Connect to Elasticsearch database on localhost:9200
es.indices.create(index='contacts', ignore=400) #Create index to store contacts if it doesn't exist

app = Flask(__name__)

@app.route('/contact', methods=['GET'])
def getContactList():
	queryParameters = request.args

	#Validate page size
	pageSize = queryParameters.get('pageSize')
	if (not pageSize):			#Default pageSize
		pageSize = 20
	else:						#Validate user pageSize
		pageSize = int(pageSize)
		if (pageSize < 0):
			return "<p>Invalid page size, must be greater than 0.</p>", 400
		elif (pageSize > 100):
			return "<p>Invalid page size, must be less than or equal to 100.</p>", 400

	#Validate page number
	pageNumber = queryParameters.get('page')
	if (not pageNumber):
		pageNumber = 0
	else:
		pageNumber = int(pageNumber)
		if (pageNumber < 0):
			return "<p>Invalid page number, must be greater than 0.</p>", 400

	#Search with optional query
	query = queryParameters.get('query')
	result = None
	if (not query):
		result = es.search(index='contacts', doc_type='contact', size=pageSize, from_=(pageSize * pageNumber))
	else:
		query = str(query)
		result = es.search(index='contacts', doc_type='contact', size=pageSize, from_=(pageSize * pageNumber), q=query)

	#result = es.search(index='contacts', doc_type='contact', size=10, from_=0, q=)
	return jsonify(result['hits']['hits']), 200

#Could move into same route as GET, and use request.method to check request type. This seems cleaner to read though
#If contact name already exists, overwrites existing contact
@app.route('/contact', methods=['POST'])
def addContact():
	name = request.form['name']

	body = {
		'name': name,
		'timestamp': datetime.now()
	}

	#Make sure document ids can be set to name (should be unique)
	result = es.index(index='contacts', doc_type='contact', id=name, body=body)
	return jsonify(result), 200

@app.route('/contact/<string:name>', methods=['GET'])
def getContact(name):
	if (not es.exists(index='contacts', doc_type='contact', id=name)):
		return "<p>Contact not found.</p>", 404

	result = es.get(index='contacts', doc_type='contact', id=name)
	return jsonify(result), 200

@app.route('/contact/<string:name>', methods=['PUT'])
def updateContact(name):
	return "<p>Update contact for " + name + "</p>", 200

@app.route('/contact/<string:name>', methods=['DELETE'])
def deleteContact(name):
	return "<p>Delete contact for " + name + "</p>", 200

app.run(debug=True)