from elasticsearch import Elasticsearch
from elasticsearch import helpers


class Database(object):

    def __init__(self, address='127.0.0.1', port=9200):
        # Connect to the elastic cluster
        self.address = address
        self.port = port
        self.es = Elasticsearch([{'host': self.address, 'port': self.port }])