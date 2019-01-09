import unittest
from elasticsearch import Elasticsearch
import api
#1. Run a Elasticstore server over localhost
#2. Run api.py connected to Elasticstore
#3. Run this script

class TestAPIMethods(unittest.TestCase):
	def test_addContact(self):
		api.addContact('Aaron', '949-949-4949', '123 A St', 'a a ron')
		api.addContact('Bbron', None, None, None)

		self.assertTrue(es.exists(index='contacts', doc_type='contact', id='Aaron'))
		self.assertTrue(es.exists(index='contacts', doc_type='contact', id='Bbron'))
		aaron = es.get(index='contacts', doc_type='contact', id='Aaron')["_source"]
		self.assertEqual(aaron['number'], '949-949-4949')
		self.assertEqual(aaron['address'], '123 A St')
		self.assertEqual(aaron['description'], 'a a ron')

	def test_getContact(self):
		api.addContact('testo', None, 'test ave.', None)
		self.assertTrue(api.getContact('testo')[1] == 200)

	def test_updateContact(self):
		api.addContact('phoneman', '8675309', 'test st', None)
		api.updateContact('phoneman', '2222222', None, 'new phone who dis')
		contactSource = es.get(index='contacts', doc_type='contact', id='phoneman')["_source"]
		self.assertEqual(contactSource['number'], '2222222')
		self.assertEqual(contactSource['address'], 'test st')
		self.assertEqual(contactSource['description'], 'new phone who dis')

	def test_deleteContact(self):
		api.addContact('evil twin', None, None, None)
		api.deleteContact('evil twin')
		self.assertTrue(not es.exists(index='contacts', doc_type='contact', id='evil twin'))

	def test_getContactList(self):
		for i in range(200):
			api.addContact(str(i), None, None, None)
		contactList = api.getContactList(20, 1, None)[0]

		#Not sure how to test the json data correctly :(
		#self.assertTrue(len(contactList) == 10)

if __name__ == '__main__':
	es = Elasticsearch()
	es.indices.delete(index='contacts', ignore=[400, 404])	#Reset index - https://stackoverflow.com/questions/35134162/elasticsearch-how-to-delete-an-index-using-python
	es.indices.create(index='contacts', ignore=400) #Create index to store contacts if it doesn't exist

	with api.app.app_context():
		unittest.main()