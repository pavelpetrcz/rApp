# -*- coding: utf-8 -*-
"""
Created on Sat Oct 17 19:26:21 2020

@author: pavel
"""
from __future__ import print_function

import json
import logging
import math
import os.path
import pickle
import re
import time
import uuid
from datetime import datetime
from pprint import pprint

import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient import discovery
from selenium import webdriver


def get_offer_json(id):
    url = "https://www.sreality.cz/api/cs/v2/estates/"

    final_url = url + id
    time.sleep(1)
    response = requests.get(final_url)
    result = response.json()
    return result


def scrape_list_of_offers():
    startingPointUrl = "https://www.sreality.cz/hledani/prodej/byty"

    # base Url
    baseUrl = "https://www.sreality.cz"

    scrapeAgain = True
    scrapeSleep = 2
    itemsPerPage = 0
    soupHtml = ""

    while scrapeAgain:
        # open chrome
        browser = webdriver.Chrome()

        # open URL
        browser.get(startingPointUrl)
        time.sleep(scrapeSleep)

        # download page in HTML
        html = browser.page_source

        # close chrome
        browser.close()

        # parse html with BS
        soupHtml = BeautifulSoup(html, "html.parser")

        # count of item in scraped page
        itemsPerPage = len(soupHtml.findAll("a", {"class": "title"}))

        # if scraping was not successful do it again slower
        if itemsPerPage == 0:
            scrapeAgain = True
            scrapeSleep += 1
        else:
            scrapeAgain = False

    # parsed URLs of all offer at page
    a = 0
    listOfUrls = []

    while itemsPerPage > a:
        parseUrlOfOfferDetail = soupHtml.findAll("a", {"class": "title"})[a]["href"]
        detailUrl = baseUrl + parseUrlOfOfferDetail
        listOfUrls.append(detailUrl)
        a = a + 1

    # concatate url for next scrape
    return listOfUrls


def extractData(data):
    # # dict pro všechny informace z nabídky
    list_offerDetailsAttr = ["internalId", "idOrder", "id", "offerName", "address", "offeredPrice", "priceNote",
                             "desc", "utilitiesCosts", "yearOfReconstruction",
                             "offerUpdatedDate", "floor", "ownership", "transferToPersonalOwnership", "location",
                             "locationDesc", "usableArea", "balconySqMeter", "terraceSqMeter", "cellarSqMeter",
                             "yearOfApproval", "water", "gas", "heating", "waste", "connectivity", "buildingCondition",
                             "building", "electricity", "transport", "roads", "energyPerformanceOfBuilding",
                             "barrieFree", "terrace", "garage", "cellar", "equipped", "parking", "loggia", "lift",
                             "sweetshopDistance", "cinemaDistance", "playgroundDistance", "culturalHeritageDistance",
                             "naturalAttractionDistance", "convenienceStoreDistance", "pubDistance", "theaterDistance",
                             "veterinaryDistance", "publicTransportDistance", "sportsGroundDistance", "tramDistance",
                             "trainDistance", "restaurantDistance", "metroDistance", "storeDistance", "schoolDistance",
                             "doctorDistance", "atmDistance", "preSchoolDistance", "schoolDistance", "pharmacyDistance",
                             "trainDistance", "postOfficeDistance"]
    dict_offerDetailsAttr = dict.fromkeys(list_offerDetailsAttr)

    # generate unique random id in hexadecimal
    g = uuid.uuid4().hex

    # # set as internal id
    dict_offerDetailsAttr["internalId"] = g

    # Name
    try:
        s_offerName = data["name"]["value"]
        dict_offerDetailsAttr["offerName"] = s_offerName
    except:
        logging.warning("s_offerName was not grabbed.", exc_info=True)
        pass

    # Address
    try:
        s_address = data["locality"]["value"]
        dict_offerDetailsAttr["address"] = s_address
    except:
        logging.warning("s_address was not grabbed.", exc_info=True)
        pass

    # price
    try:
        s_offeredPrice = data["price_czk"]["value_raw"]
    except:
        s_offeredPrice = 000000000
        logging.warning("s_offeredPrice was not grabbed.", exc_info=True)
        pass
    dict_offerDetailsAttr["offeredPrice"] = s_offeredPrice

    # Description
    s_desc = data["text"]["value"]
    dict_offerDetailsAttr["desc"] = s_desc

    # Parsing additional data from table below description
    # =====================================================
    d = data["items"]
    dict_detailsTableOfOffer = convertToKeyValue(d, "name", "value", False)

    # if offer was updated today, they state "today" instead of date therefore ...
    now = datetime.now()
    if dict_detailsTableOfOffer['Aktualizace'] == "Dnes":
        dict_offerDetailsAttr['offerUpdatedDate'] = now.strftime("%d/%m/%Y")

        # if update is date, we use that formatted date
    else:
        dtime = parse(str(dict_detailsTableOfOffer['Aktualizace']))
        dict_offerDetailsAttr['offerUpdatedDate'] = dtime.strftime("%d/%m/%Y")

    # Parsing of values from table
    dict_detailsAttr_binding = {
        "usableArea" : "Užitná plocha",
        "terraceSqMeter" : "Terasa",
        "terrace": "Terasa",
        "cellarSqMeter" : "Sklep",
        "cellar": "Sklep",
        "priceNote" : "Poznámka k ceně",
        "location" : "Umístění objektu",
        "floor" : "Podlaží",
        "building" : "Stavba",
        "buildingCondition" : "Stav objektu",
        "lift" : "Výtah",
        "ownership" : "Vlastnictví",
        "id" : "ID zakázky",
        "idOrder" : "ID",
        "energyPerformanceOfBuilding": "Energetická náročnost budovy",
        "transport" : "Doprava",
        "roads" : "Komunikace",
        "barrieFree" : "Bezbariérový",
        "parking" : "Parkování",
        "garage" : "Garáž",
        "equipped" : "Vybavení",
        "transferToPersonalOwnership" : "Převod do OV",
        "yearOfApproval" : "Rok kolaudace"
    }

    # go through all attributes
    for key,value in dict_detailsAttr_binding.items():
        try:
            dict_offerDetailsAttr[key] = dict_detailsTableOfOffer[value]
        except:
            logging.warning(key + " was not grabbed.", exc_info=True)

    # specific types of attribues
    try:
        s_water = dict_detailsTableOfOffer['Voda']["value"]
        dict_offerDetailsAttr['water'] = s_water
    except:
        logging.warning("s_water was not grabbed.", exc_info=True)
        pass
    try:
        s_gas = dict_detailsTableOfOffer['Plyn']["value"]
        dict_offerDetailsAttr['gas'] = s_gas
    except:
        logging.warning("s_gas was not grabbed.", exc_info=True)
        pass
    try:
        s_heating = dict_detailsTableOfOffer['Topení']["value"]
        dict_offerDetailsAttr['heating'] = s_heating
    except:
        logging.warning("s_heating was not grabbed.", exc_info=True)
        pass
    try:
        s_waste = dict_detailsTableOfOffer['Odpad']["value"]
        dict_offerDetailsAttr['waste'] = s_waste
    except:
        logging.warning("s_waste was not grabbed.", exc_info=True)
        pass
    try:
        s_electricity = dict_detailsTableOfOffer['Elektřina']["value"]
        dict_offerDetailsAttr['electricity'] = s_electricity
    except:
        logging.warning("s_electricity was not grabbed.", exc_info=True)
        pass

    # Parsing of distances from json object
    try:
        dist = data["poi"]
        dict_poi = convertToKeyValue(dist, "name", "distance", True)
    except KeyError:
        logging.info("Offer does not contains POI data.")

    dict_distance_binding = {
        "playgroundDistance" : "Hřiště",
        "culturalHeritageDistance" : "Kulturní památka",
        "publicTransportDistance" : "Bus MHD",
        "sportsGroundDistance" : "Sportoviště",
        "tramDistance" : "Tram",
        "metroDistance" : "Metro",
        "trainDistance" : "Vlak",
        "sweetshopDistance" : "Cukrárna",
        "cinemaDistance" : "Kino",
        "convenienceStoreDistance" : "Večerka",
        "pubDistance" : "Hospoda",
        "theaterDistance" : "Divadlo",
        "veterinaryDistance" : "Veterinář",
        "restaurantDistance" : "Restaurace",
        "schoolDistance" : "Škola",
        "postOfficeDistance" : "Pošta",
        "storeDistance" : "Obchod",
        "pharmacyDistance" : "Lékárna",
        "atmDistance" : "Bankomat",
        "doctorDistance" : "Lékař",
        "preSchoolDistance" : "Školka",
        "naturalAttractionDistance" : "Přírodní zajímavost"
    }

    for key, value in dict_distance_binding.items():
        try:
            dict_offerDetailsAttr[key] = dict_poi[value]
        except:
            logging.warning(key + " was not grabbed.", exc_info=True)

    print(dict_offerDetailsAttr)


    # # oAuth 2.0 Google
    # creds = None
    #
    # # If modifying these scopes, delete the file token.pickle.
    # SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    #
    # if os.path.exists('token.pickle'):
    #     with open('token.pickle', 'rb') as token:
    #         creds = pickle.load(token)
    # # If there are no (valid) credentials available, let the user log in.
    # if not creds or not creds.valid:
    #     if creds and creds.expired and creds.refresh_token:
    #         creds.refresh(Request())
    #     else:
    #         flow = InstalledAppFlow.from_client_secrets_file(
    #             'C:\\Users\\pavel\\Disk Google\\finance\\nemovitosti\\nemovitostiSecretOauth.json', SCOPES)
    #         creds = flow.run_local_server(port=8000)
    #     # Save the credentials for the next run
    #     with open('token.pickle', 'wb') as token:
    #         pickle.dump(creds, token)
    #
    # service = discovery.build('sheets', 'v4', credentials=creds)
    #
    # # The ID of the spreadsheet to update.
    # spreadsheet_id = '1YPWOsBVm2qGOWJx4dgniopZ_Ekm91h7hxy2-enof7N8'
    #
    # # Values will be appended after the last row of the table.
    # range_ = 'A1:BL2'
    #
    # # How the input data should be interpreted.
    # value_input_option = 'RAW'
    #
    # # How the input data should be inserted.
    # insert_data_option = 'INSERT_ROWS'
    #
    # value_range_body = {"values": [["a", "b"]], "range": "A1:BL2"}
    #
    # request = service.spreadsheets().values().append(spreadsheetId=spreadsheet_id, range=range_,
    #                                                  valueInputOption=value_input_option,
    #                                                  insertDataOption=insert_data_option, body=value_range_body)
    # response = request.execute()
    #
    # pprint(response)
    # print("offerSaved")


def getStringFromList(input, field):
    """
      :param input: list of all items
      :param field: name of field where search
      :return: string of values separated by comma
      """
    separator = ', '
    for i in input[field]:
        x = i["value"]
        y = []
        y.append(x)
    return separator.join(y)


def convertToKeyValue(data, keyfield, valueField, roundDown):
    """
      :param keyfield: name of field to become key of dict
      :param valueField: name of field to become value of dict
      :param roundDown: if value is numeric, you can round down (True)
      :param data: list with data to convert
      :return: dict with key:value data
      """
    dict_result = {}
    for i in data:
        key = i[keyfield]
        value = i[valueField]
        if (roundDown):
            value = math.floor(value)
        else:
            continue
        dict_result[key] = value
    return dict_result