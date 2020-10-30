# -*- coding: utf-8 -*-
"""
Created on Sat Oct 17 19:26:21 2020

@author: pavel
"""
from __future__ import print_function

import json
import logging
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

    while (scrapeAgain):
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
        if (itemsPerPage == 0):
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
    # set now
    #time_now = datetime.fromtimestamp(time.time())
    dict_detailsTableOfOffer = {}
    d = data["items"]
    for i in d:
        key = i["name"]
        value = i["value"]
        dict_detailsTableOfOffer[key] = value

    # # if offer was updated today, they state "today" instead of date therefore ...
    # if dict_table_of_att['Aktualizace'] == "Dnes":
    #     dict_offerDetailsAttr['offerUpdatedDate'] = time_now.strftime("%d/%m/%Y")
    #
    #     # if update is date, we use that formatted date
    # else:
    #     dtime = parse(str(dict_table_of_att['Aktualizace']))
    #     dict_offerDetailsAttr['offerUpdatedDate'] = dtime.strftime("%d/%m/%Y")


    # Parsing of values from table
    try:
        s_usableArea = dict_detailsTableOfOffer['Užitná plocha']
        dict_offerDetailsAttr['usableArea'] = s_usableArea
    except:
        logging.warning("s_usableArea was not grabbed.", exc_info=True)
        pass
    try:
        s_terraceSqMeter = dict_detailsTableOfOffer['Terasa']
        dict_offerDetailsAttr['terraceSqMeter'] = s_terraceSqMeter
    except:
        logging.warning("s_terraceSqMeter was not grabbed.", exc_info=True)
        pass
    try:
        s_cellarSqMeter = dict_detailsTableOfOffer['Sklep']
        dict_offerDetailsAttr['cellarSqMeter'] = s_cellarSqMeter
    except:
        logging.warning("s_cellarSqMeter was not grabbed.", exc_info=True)
        pass
    try:
        s_priceNote = dict_detailsTableOfOffer['Poznámka k ceně']
        dict_offerDetailsAttr['priceNote'] = s_priceNote
    except:
        logging.warning("s_priceNote was not grabbed.", exc_info=True)
        pass
    try:
        s_location = dict_detailsTableOfOffer['Umístění objektu']
        dict_offerDetailsAttr['location'] = s_location
    except:
        logging.warning("s_location was not grabbed.", exc_info=True)
        pass
    try:
        s_floor = dict_detailsTableOfOffer['Podlaží']
        dict_offerDetailsAttr['floor'] = s_floor
    except:
        logging.warning("s_floor was not grabbed.", exc_info=True)
        pass
    try:
        s_building = dict_detailsTableOfOffer['Stavba']
        dict_offerDetailsAttr['building'] = s_building
    except:
        logging.warning("s_building was not grabbed.", exc_info=True)
        pass
    try:
        s_buildingCondition = dict_detailsTableOfOffer['Stav objektu']
        dict_offerDetailsAttr['buildingCondition'] = s_buildingCondition
    except:
        logging.warning("s_buildingCondition was not grabbed.", exc_info=True)
        pass
    try:
        s_lift = dict_detailsTableOfOffer['Výtah']
        dict_offerDetailsAttr['lift'] = s_lift
    except:
        logging.warning("s_lift was not grabbed.", exc_info=True)
        pass
    try:
        s_ownership = dict_detailsTableOfOffer['Vlastnictví']
        dict_offerDetailsAttr['ownership'] = s_ownership
    except:
        logging.warning("s_ownership was not grabbed.", exc_info=True)
        pass
    try:
        s_id = dict_detailsTableOfOffer['ID zakázky']
        dict_offerDetailsAttr['id'] = s_id
    except:
        logging.warning("s_id was not grabbed.", exc_info=True)
        pass
    try:
        s_idOrder = dict_detailsTableOfOffer['ID']
        dict_offerDetailsAttr['idOrder'] = s_idOrder
    except:
        logging.warning("s_idOrder was not grabbed.", exc_info=True)
        pass
    try:
        s_energyPerformanceOfBuilding = dict_detailsTableOfOffer['Energetická náročnost budovy']
        dict_offerDetailsAttr['energyPerformanceOfBuilding'] = s_energyPerformanceOfBuilding
    except:
        logging.warning("s_energyPerformanceOfBuilding was not grabbed.", exc_info=True)
        pass
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
    try:
        s_connectivity = dict_detailsTableOfOffer['Telekomunikace']
        dict_offerDetailsAttr['connectivity'] = s_connectivity
    except:
        logging.warning("s_connectivity was not grabbed.", exc_info=True)
        pass
    try:
        separator = ', '
        for i in dict_detailsTableOfOffer['Doprava']:
            x = i["value"]
            y.append(x)
        s_transport = separator.join(y)
        print(s_transport)
        dict_offerDetailsAttr['transport'] = s_transport
    except:
        logging.warning("s_transport was not grabbed.", exc_info=True)
        pass
    try:
        separator = ', '
        for i in dict_detailsTableOfOffer['Komunikace']:
            x = i["value"]
            z.append(x)
        s_roads = separator.join(z)
        print(s_roads)
        dict_offerDetailsAttr['roads'] = s_roads
    except:
        logging.warning("s_roads was not grabbed.", exc_info=True)
        pass
    try:
        s_barrieFree = dict_detailsTableOfOffer['Bezbariérový']
        dict_offerDetailsAttr['barrieFree'] = s_barrieFree
    except:
        logging.warning("s_barrieFree was not grabbed.", exc_info=True)
        pass
    try:
        s_parking = dict_detailsTableOfOffer['Parkování']
        dict_offerDetailsAttr['parking'] = s_parking
    except:
        logging.warning("s_parking was not grabbed.", exc_info=True)
        pass
    # try:
    #     dict_offerDetailsAttr['terrace'] = dict_table_of_att['Terasa']
    # except:
    #     pass
    # try:
    #     dict_offerDetailsAttr['cellar'] = dict_table_of_att['Sklep']
    # except:
    #     pass
    # try:
    #     dict_offerDetailsAttr['garage'] = dict_table_of_att['Garáž']
    # except:
    #     pass
    # try:
    #     dict_offerDetailsAttr['equipped'] = dict_table_of_att['Vybavení']
    # except:
    #     pass
    try:
        s_transferToPersonalOwnership = dict_detailsTableOfOffer['Převod do OV']
        dict_offerDetailsAttr['transferToPersonalOwnership'] = s_transferToPersonalOwnership
    except:
        logging.warning("s_transferToPersonalOwnership was not grabbed.", exc_info=True)
        pass
    try:
        s_yearOfApproval = dict_detailsTableOfOffer['Rok kolaudace']
        dict_offerDetailsAttr['yearOfApproval'] = s_yearOfApproval
    except:
        logging.warning("s_yearOfApproval was not grabbed.", exc_info=True)
        pass

    #print(dict_offerDetailsAttr)

    # Parsing of distances
    # try:
    #     s_playgroundDistance = dict_detailsTableOfOffer['Hřiště']
    #     dict_offerDetailsAttr['playgroundDistance'] = s_playgroundDistance
    # except:
    #     logging.warning("s_playgroundDistance was not grabbed.", exc_info=True)
    #     pass
    # try:
    #     dict_offerDetailsAttr['culturalHeritageDistance'] = dict_table_of_att['Kulturní památka']
    # except:
    #     pass
    # try:
    #     dict_offerDetailsAttr['publicTransportDistance'] = dict_table_of_att['Bus MHD']
    # except:
    #     pass
    # try:
    #     dict_offerDetailsAttr['sportsGroundDistance'] = dict_table_of_att['Sportoviště']
    # except:
    #     pass
    # try:
    #     dict_offerDetailsAttr['tramDistance'] = dict_table_of_att['Tram']
    # except:
    #     pass
    # try:
    #     dict_offerDetailsAttr['metroDistance'] = dict_table_of_att['Metro']
    # except:
    #     pass
    # try:
    #     dict_offerDetailsAttr['trainDistance'] = dict_table_of_att['Vlak']
    # except:
    #     pass
    # try:
    #     dict_offerDetailsAttr['sweetshopDistance'] = dict_table_of_att['Cukrárna']
    # except:
    #     pass
    # try:
    #     dict_offerDetailsAttr['cinemaDistance'] = dict_table_of_att['Kino']
    # except:
    #     pass
    # try:
    #     dict_offerDetailsAttr['convenienceStoreDistance'] = dict_table_of_att['Večerka']
    # except:
    #     pass
    # try:
    #     dict_offerDetailsAttr['pubDistance'] = dict_table_of_att['Hospoda']
    # except:
    #     pass
    # try:
    #     dict_offerDetailsAttr['theaterDistance'] = dict_table_of_att['Divadlo']
    # except:
    #     pass
    # try:
    #     dict_offerDetailsAttr['veterinaryDistance'] = dict_table_of_att['Veterinář']
    # except:
    #     pass
    # try:
    #     dict_offerDetailsAttr['restaurantDistance'] = dict_table_of_att['Restaurace']
    # except:
    #     pass
    # try:
    #     dict_offerDetailsAttr['schoolDistance'] = dict_table_of_att['Škola']
    # except:
    #     pass
    # try:
    #     dict_offerDetailsAttr['postOfficeDistance'] = dict_table_of_att['Pošta']
    # except:
    #     pass
    # try:
    #     dict_offerDetailsAttr['storeDistance'] = dict_table_of_att['Obchod']
    # except:
    #     pass
    # try:
    #     dict_offerDetailsAttr['trainDistance'] = dict_table_of_att['Vlak']
    # except:
    #     pass
    # try:
    #     dict_offerDetailsAttr['pharmacyDistance'] = dict_table_of_att['Lékárna']
    # except:
    #     pass
    # try:
    #     dict_offerDetailsAttr['atmDistance'] = dict_table_of_att['Bankomat']
    # except:
    #     pass
    # try:
    #     dict_offerDetailsAttr['doctorDistance'] = dict_table_of_att['Lékař']
    # except:
    #     pass
    # try:
    #     dict_offerDetailsAttr['preSchoolDistance'] = dict_table_of_att['Školka']
    # except:
    #     pass
    # try:
    #     dict_offerDetailsAttr['naturalAttractionDistance'] = dict_table_of_att['Přírodní zajímavost']
    # except:
    #     pass
    #
    # list_offerDetailValues = dict_offerDetailsAttr.values()
    #
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
