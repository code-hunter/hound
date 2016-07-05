import pymongo
import time
from hound.common.exception import InvalidDBConnString
from hound.common.logger import get_logger

LOG = get_logger(__name__)

class MongodbClient(object):

    def __init__(self, conn_str=None, host=None, port=27017, database_name=None, collection_name=None):

        self.conn_str = conn_str
        self.host = host
        self.port = port
        self.database_name = database_name
        self.collection_name = collection_name

        if conn_str and isinstance(conn_str,str):
            self._parse_conn_str(conn_str)

        self.client = pymongo.MongoClient(host=self.host, port=int(self.port))
        self.database = self.client[self.database_name]
        self.collection = self.database[self.collection_name]

    def _parse_conn_str(self, conn_str):
        '''parse mongodb conn string format: mongodb://localhost:27017/database/collection'''

        if not conn_str.startswith('mongodb'):
            LOG.error('invalid mongodb connectiong: ' + conn_str)
            raise InvalidDBConnString

        try:

            conn_str = conn_str.split('//')[1]

            conn_splits = conn_str.split('/')
            host_port = conn_splits[0].split(':')
            self.host = host_port[0]
            self.port = host_port[1]
            self.database_name = conn_splits[1]
            self.collection_name = conn_splits[2]

        except Exception as e:
            LOG.error('invalid mongodb connectiong: ' + conn_str)
            raise InvalidDBConnString


    def create(self, doc={}, id=None):
        if not isinstance(doc, dict):
            doc = doc.as_dict()
        doc['create_time'] = time.time()
        self.collection.insert(doc)

# mongoConn = "mongodb://localhost:27017/hunter/archive"

