import time
from hound.common.exception import InvalidDBConnString
from hound.common.logger import get_logger
from elasticsearch import Elasticsearch

LOG = get_logger(__name__)

class  ESClient(object):

    def __init__(self, conn_str=None, hosts=None, port=9300, index=None, type=None):
        self.conn_str = conn_str
        self.hosts = hosts
        self.port= port
        self.index = index
        self.type = type
        self.client = None

        if conn_str and isinstance(conn_str,str):
            self._parse_conn_str(conn_str)
        if self.hosts and isinstance(self.hosts, list):
            self.client = Elasticsearch(hosts=self.hosts)
        if self.client:
            self.client.indices.create(index=self.index, ignore=400)

    def _parse_conn_str(self, conn_str):
        '''parse elasticsearch conn string format: elasticsearch://localhost:9300/cluster_name/index_name/type_name'''

        if not conn_str.startswith('elasticsearch'):
            LOG.error('invalid elasticsearch connectiong: ' + conn_str)
            raise InvalidDBConnString

        try:
            conn_str = conn_str.split('//')[1]
            conn_splits = conn_str.split('/')
            hosts_port = conn_splits[0].split(':')
            self.hosts = list(hosts_port[0].split(','))
            self.port = hosts_port[1]
            self.cluster = conn_splits[1]
            self.index = conn_splits[2]
            self.type = conn_splits[3]
        except Exception as e:
            LOG.error('invalid elasticsearch connectiong: ' + conn_str)
            raise InvalidDBConnString

    def create(self, doc={}, id=None):
        if not isinstance(doc, dict):
            doc = doc.as_dict()
        doc['create_time'] = time.time()
        return self.client.index(index=self.index, doc_type=self.type, body= doc, id=id)


# client = ESClient(conn_str="elasticsearch://localhost:9300/cluster_name/index_name/type_name")

