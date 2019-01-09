from flask import Flask, jsonify, request
from elasticsearch import Elasticsearch
from datetime import datetime

es = Elasticsearch() #Connect to Elasticsearch database on localhost:9200
es.indices.create(index='contacts', ignore=400) #Create index to store contacts if it doesn't exist

app = Flask(__name__)

@app.route('/contact', methods=['GET'])
def getContactListHandler():
	queryParameters = request.args

	pageSize = queryParameters.get('pageSize')
	pageNumber = queryParameters.get('page')
	query = queryParameters.get('query')

	return getContactList(es, pageSize, pageNumber, query)

@app.route('/contact', methods=['POST']) #Could move into same route as GET, and use request.method to check request type.
def addContactHandler():
	#Required
	name = request.form['name']
	#name = str(name) 			The name is stored as unicode, change to string???

	#Optional
	number = request.form.get('number')
	address = request.form.get('address')
	description = request.form.get('description')

	return addContact(name, number, address, description)

@app.route('/contact/<string:name>', methods=['GET'])
def getContactHandler(name):
	return getContact(name)

@app.route('/contact/<string:name>', methods=['PUT'])
def updateContactHandler(name):
	number = request.form.get('number')
	address = request.form.get('address')
	description = request.form.get('description')

	return updateContact(name, number, address, description)

@app.route('/contact/<string:name>', methods=['DELETE'])
def deleteContactHandler(name):
	return deleteContact(name)


def getContactList(pageSize, pageNumber, query):
	#Validate page size
	if (not pageSize):			#Default pageSize
		pageSize = 20
	else:						#Validate user pageSize
		pageSize = int(pageSize)
		if (pageSize < 0):
			return "<p>Invalid page size, must be greater than 0.</p>", 400
		elif (pageSize > 100):
			return "<p>Invalid page size, must be less than or equal to 100.</p>", 400

	#Validate page number
	if (not pageNumber):
		pageNumber = 0
	else:
		pageNumber = int(pageNumber)
		if (pageNumber < 0):
			return "<p>Invalid page number, must be greater than 0.</p>", 400

	#Search with optional query
	#Possible improvement: Sort query results alphabetically
	result = None
	if (not query):
		result = es.search(index='contacts', doc_type='contact', size=pageSize, from_=(pageSize * pageNumber))
	else:
		query = str(query)
		result = es.search(index='contacts', doc_type='contact', size=pageSize, from_=(pageSize * pageNumber), q=query)
	return jsonify(result['hits']['hits']), 200

def addContact(name, number, address, description):
	#Dont overwrite existing contact
	if (es.exists(index='contacts', doc_type='contact', id=name)):
		return "Contact name already exists.", 400

	##if (not validatePhoneNumber(number)):
	##	number = None
	##if (not validateAddress(address)):
	##	address = None
	##if (not validateDescription(description)):
	##	description = None

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

def getContact(name):
	if (not es.exists(index='contacts', doc_type='contact', id=name)):
		return "<p>Contact not found.</p>", 404

	result = es.get(index='contacts', doc_type='contact', id=name)
	return jsonify(result), 200

def updateContact(name, number, address, description):
	if (not es.exists(index='contacts', doc_type='contact', id=name)):
		return "<p>Contact not found.</p>", 400

	##if (not validatePhoneNumber(number)):
	##	number = None
	##if (not validateAddress(address)):
	##	address = None
	##if (not validateDescription(description)):
	##	description = None

	#Update body with values given
	body = es.get(index='contacts', doc_type='contact', id=name)["_source"]
	if (number):
		body['number'] = number
	if (address):
		body['address'] = address
	if (description):
		body['description'] = description

	#Overwrite existing entry
	result = es.index(index='contacts', doc_type='contact', id=name, body=body)

	return jsonify(result), 200

def deleteContact(name):
	if (not es.exists(index='contacts', doc_type='contact', id=name)):
		return "<p>Contact not found.</p>", 400

	result = es.delete(index='contacts', doc_type='contact', id=name)
	return "<p>Deleted contact for " + name + "</p>", 200

if __name__ == '__main__':
	app.run(debug=True)