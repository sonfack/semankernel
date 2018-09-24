from elasticsearch import Elasticsearch
from elasticsearch import helpers


class Database(object):

    def __init__(self, address='172.17.0.2', port=9200):
        # Connect to the elastic cluster
        self.address = address
        self.port = port
        self.es = Elasticsearch([{'host': self.address, 'port': self.port}])