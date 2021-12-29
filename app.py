import requests as re
import json
import time
import logging
import os

import actions

"""
Created on Sat Oct 17 19:32:08 2020

@author: pavel
"""

if __name__ == "__main__":
    again = True
    dbConnNotEstablished = True

    # logging setup
    logging.basicConfig(
        filename='app.log',
        filemode='w',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    while again:
        try:
            estates_list = re.get(
                'http://sreality.cz/api/cs/v2/estates?category_main_cb=1&category_type_cb=1&locality_region_id=1&per_page=10&tms=1640380327573')
            estates_list = json.loads(estates_list.text)
            estates = estates_list['_embedded']['estates']

            estateIds = []
            for estate in estates:
                estateIds.append(estate['hash_id'])

            if len(estateIds) > 0 and dbConnNotEstablished:
                conn_string = 'mongodb+srv://ppetr:{}@clusterppe.hga2z.mongodb.net/estates?retryWrites=true&w=majority'.format(
                    os.environ['db_pass'])
                clientDb = actions.getDbConn(connection_string=conn_string)
                collection_name = clientDb["flats"]

            for estateId in estateIds:
                url = "https://www.sreality.cz/api/cs/v2/estates/{}?tms=1640382199242".format(estateId)
                estate_detail_offer = re.get(url)
                dict_estate_detail_offer = json.loads(estate_detail_offer.text)

                objects_to_delete = ['map',
                                     'meta_description',
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

                collection_name.insert_one(dict_estate_detail_offer)

                time.sleep(10)

        except Exception:
            logging.warning('Offer was not saved.', stack_info=True)
            continue
