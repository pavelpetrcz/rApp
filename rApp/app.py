# -*- coding: utf-8 -*-
"""
Created on Sat Oct 17 19:32:08 2020

@author: pavel
"""

import actions

if __name__ == "__main__":
    # scrape firt page of offers
    listOfOffers = actions.scrapeListOfOffers()

    #for each url of offer try to scrape html and then extract data
    for item in listOfOffers:
        # scrape specific offer
        scraped_html = actions.scrapeOfferHtml(item)
        actions.extractData(scraped_html)