# -*- coding: utf-8 -*-
"""
Created on Sat Oct 17 19:32:08 2020

@author: pavel
"""

import actions

if __name__ == "__main__":
    
    # scrape firt page of offers
    ba = actions.scrapeListOfOffers()
    
    # scrape specific offer
    actions.scrapeOffer(ba)