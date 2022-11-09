import random
import uuid

from pymongo import MongoClient

class MongoDBConnection():

    def __init__(self, username, password, hostname, port=27017):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.client = None

    def __enter__(self):
        CONNECTION_STRING = f"mongodb://{self.username}:{self.password}@" \
                            f"{self.hostname}:{self.port}"
        self.client = MongoClient(CONNECTION_STRING)
        self.db = self.client['test1']
        return self.db

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.client.close()


if __name__ == '__main__':
    with MongoDBConnection('admin', 'admin', '127.0.0.1') as db:
        # db.create_collection("stop_points")
        # collection = db['stop_points']
        # collection.insert_one({'points': [{'name': f'point_{uuid.uuid4()}',
        #                                    'lat': random.random(),
        #                                    'lon': random.random()}
        #                                  ]})
        # db.create_collection("event_users")
        collection = db['event_users']
        collection.insert_one({'pending': [7], 'accepted': [6]})



