#  Copyright (c) Pavel Petr 2021.
import logging
import time

from pymongo import MongoClient

import requests as re
import json


def getDbConn(connection_string):
    """
    create connection to MongoDB
    :param connection_string: insert specified URI to MongoDB database location
    :return: client - object at which you can choose collection from "estates" database
    """
    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    client = MongoClient(connection_string)
    # Create the database for our example (we will use the same database throughout the tutorial
    return client['estates']


def scrapeContent(collection_name):
    """
    Method extract list of 100 lastly added estates an save each of them to DB
    :param collection_name: insert object from mongo client with specified collection where to store data
    """
    try:
        # get list of estates
        estates_list = re.get(
            'http://sreality.cz/api/cs/v2/estates?category_main_cb=1&category_type_cb=1&locality_region_id=1&per_page=10&tms=1640380327573')
        estates_list = json.loads(estates_list.text)
        estates = estates_list['_embedded']['estates']

        estateIds = []
        for estate in estates:
            estateIds.append(estate['hash_id'])

        # get detail of estate and save
        for estateId in estateIds:
            url = "https://www.sreality.cz/api/cs/v2/estates/{}?tms=1640382199242".format(estateId)
            estate_detail_offer = re.get(url)
            dict_estate_detail_offer = json.loads(estate_detail_offer.text)

            # delete unwated objects from json
            objects_to_delete = ['meta_description',
                                 '_embedded',
                                 'logged_in',
                                 'is_topped',
                                 '_links',
                                 'panorama',
                                 'seo',
                                 'rus',
                                 'is_topped_today',
                                 'locality_district_id',
                                 'codeItems'
                                 ]

            for obj in objects_to_delete:
                del dict_estate_detail_offer[obj]
            del dict_estate_detail_offer['map']['geometry']

            # save to DB
            collection_name.insert_one(dict_estate_detail_offer)

            # wait a while to scrape next
            time.sleep(10)

    except Exception as exce:
        logging.warning(exce, stack_info=True, exc_info=True)
