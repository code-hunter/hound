from hound.common.exception import *
from .es import ESClient

def get_db_client(db_conn):

    if db_conn.startswith('elasticsearch'):
        return ESClient(db_conn)
    elif db_conn.startswith('mysql'):
        raise NotImplementedError
    else:
        raise InvalidDBConnString