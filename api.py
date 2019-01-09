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
	#Possible improvement: Sort query results alphabetically
	query = queryParameters.get('query')
	result = None
	if (not query):
		result = es.search(index='contacts', doc_type='contact', size=pageSize, from_=(pageSize * pageNumber))
	else:
		query = str(query)
		result = es.search(index='contacts', doc_type='contact', size=pageSize, from_=(pageSize * pageNumber), q=query)

	#result = es.search(index='contacts', doc_type='contact', size=10, from_=0, q=)
	return jsonify(result['hits']['hits']), 200

@app.route('/contact', methods=['POST']) #Could move into same route as GET, and use request.method to check request type.
def addContact():
	#Required
	name = request.form['name']
	#name = str(name) 			The name is stored as unicode, change to string???

	#Optional
	number = request.form.get('number')
	address = request.form.get('address')
	description = request.form.get('description')

	#Dont overwrite existing contact
	if (es.exists(index='contacts', doc_type='contact', id=name)):
		return "Contact name already exists.", 400

	body = {
		'name': name,
		'number': number,
		'address': address,
		'description': description,
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
	if (not es.exists(index='contacts', doc_type='contact', id=name)):
		return "<p>Contact not found.</p>", 400

	result = es.get(index='contacts', doc_type='contact', id=name)

	#Update body with values given
	body = es.get(index='contacts', doc_type='contact', id=name)["_source"]
	number = request.form.get('number')
	if (number):
		body['number'] = number
	address = request.form.get('address')
	if (address):
		body['address'] = address
	description = request.form.get('description')
	if (description):
		body['description'] = description

	#Overwrite existing entry
	result = es.index(index='contacts', doc_type='contact', id=name, body=body)

	return jsonify(result), 200

@app.route('/contact/<string:name>', methods=['DELETE'])
def deleteContact(name):
	if (not es.exists(index='contacts', doc_type='contact', id=name)):
		return "<p>Contact not found.</p>", 400

	result = es.delete(index='contacts', doc_type='contact', id=name)
	return "<p>Deleted contact for " + name + "</p>", 200

app.run(debug=True)