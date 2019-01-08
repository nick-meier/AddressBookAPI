from flask import Flask, jsonify, request

app = Flask(__name__)

#Replace with an elasticstore database
contacts = [
    {'id': 0,
     'name': 'Nick'},
    {'id': 1,
     'name': 'Aaron'},
    {'id': 2,
     'name': 'Ben'}
]

@app.route('/contact', methods=['GET'])
def getContactList():
	return "<p>Contact List</p>", 200

#Could move into same route as GET, and use request.method to check request type
@app.route('/contact', methods=['POST'])
def addContact():
	return "<p>Add a new contact</p>", 200

@app.route('/contact/<string:name>', methods=['GET'])
def getContact(name):
	return "<p>User Contact Page for " + name + "</p>", 200

@app.route('/contact/<string:name>', methods=['PUT'])
def updateContact(name):
	return "<p>Update contact for " + name + "</p>", 200

@app.route('/contact/<string:name>', methods=['DELETE'])
def deleteContact(name):
	return "<p>Delete contact for " + name + "</p>", 200

app.run(debug=True)