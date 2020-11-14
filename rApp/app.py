# -*- coding: utf-8 -*-
"""
Created on Sat Oct 17 19:32:08 2020

@author: pavel
"""

import extractDataFromOfferFlow
import extractOffersFromPageFlow
import extractOffersUrlsAndCheckNextPageFlow
import logging

if __name__ == "__main__":
    # logging setup
    logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

    # get URL of offers at page
    l, ex = extractOffersUrlsAndCheckNextPageFlow.execute()

    # get JSON of offers at page
    data = extractOffersFromPageFlow.execute(l)

    # from each JSON extract data and save them
    for j in data:
        extractDataFromOfferFlow.execute(j)
