# -*- coding: utf-8 -*-
"""
Created on Sat Oct 17 19:32:08 2020

@author: pavel
"""

import acts

if __name__ == "__main__":
    # scrape first page of offers
    listOfOffers = acts.scrape_list_of_offers()
    print(listOfOffers)
    list_d = []

    for item in listOfOffers:
        splitedItem = item.split("/")
        data = acts.get_offer_json(splitedItem[-1])
        list_d.append(data)

    for i in list_d:
        acts.extractData(i)
        print(i["meta_description"])
