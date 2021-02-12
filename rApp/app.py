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
    baseUrl = "https://www.sreality.cz"
    url = "https://www.sreality.cz/hledani/prodej/byty/jihocesky-kraj?stari=dnes"
    again = True
    # logging setup
    logging.basicConfig(filename='app.log', filemode='w', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # get URL of offers at page
    while again:
        l, ex, newUrl = extractOffersUrlsAndCheckNextPageFlow.execute(url)
        again = ex
        url = baseUrl + newUrl

        # get JSON of offers at page
        data = extractOffersFromPageFlow.execute(l)

        # from each JSON extract data and save them
        for j in data:
            extractDataFromOfferFlow.execute(j)
