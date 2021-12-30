from pymongo import MongoClient


def getDbConn(connection_string):
    """
    create connection to MongoDB
    :param connection_string:
    :return: client - object at which you can choose collection from "estates" database
    """
    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    client = MongoClient(connection_string)
    # Create the database for our example (we will use the same database throughout the tutorial
    return client['estates']
