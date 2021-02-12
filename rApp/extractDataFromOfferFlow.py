# -*- coding: utf-8 -*-
"""
Created on Sat Oct 17 19:26:21 2020

@author: pavel
"""
from __future__ import print_function

import actions
import logging
import os.path
import pickle
import uuid

from datetime import date
from datetime import timedelta

from dateutil.parser import parse
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient import discovery


def execute(data):
    # list of all attributes
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
                             "trainDistance", "postOfficeDistance", "lat", "lon"]
    dict_offerDetailsAttr = dict.fromkeys(list_offerDetailsAttr)

    # # set as internal id
    dict_offerDetailsAttr["internalId"] = uuid.uuid4().hex

    # Name
    try:
        s_offerName = data["name"]["value"]
        dict_offerDetailsAttr["offerName"] = s_offerName
    except KeyError:
        logging.warning("s_offerName was not grabbed.", exc_info=True)
        pass

    # Address
    try:
        s_address = data["locality"]["value"]
        dict_offerDetailsAttr["address"] = s_address
    except KeyError:
        logging.warning("s_address was not grabbed.", exc_info=True)
        pass

    # Price
    try:
        s_offeredPrice = data["price_czk"]["value_raw"]
    except KeyError:
        s_offeredPrice = 000000000
        logging.warning("s_offeredPrice was not grabbed.", exc_info=True)
        pass
    dict_offerDetailsAttr["offeredPrice"] = s_offeredPrice

    # Description
    s_desc = data["text"]["value"]
    dict_offerDetailsAttr["desc"] = s_desc

    # GPS coordinates
    s_lat = data["map"]["lat"]
    dict_offerDetailsAttr["lat"] = s_lat
    s_lon = data["map"]["lon"]
    dict_offerDetailsAttr["lon"] = s_lon

    # Parsing additional data from table below description
    d = data["items"]
    dict_detailsTableOfOffer = actions.convertToKeyValue(d, "name", "value", False)

    # set update date of offer
    today = date.today()
    yesterday = today - timedelta(days=1)
    if dict_detailsTableOfOffer['Aktualizace'] == "Dnes":
        dateOfUpdate = today
    elif dict_detailsTableOfOffer['Aktualizace'] == "Včera":
        dateOfUpdate = yesterday
    else:
        dateOfUpdate = parse(str(dict_detailsTableOfOffer['Aktualizace']))

    dict_offerDetailsAttr['offerUpdatedDate'] = dateOfUpdate.strftime("%d/%m/%Y")

    # Parsing of values from table with details of offer
    dict_detailsAttr_binding = {
        "usableArea": "Užitná plocha",
        "terraceSqMeter": "Terasa",
        "terrace": "Terasa",
        "cellarSqMeter": "Sklep",
        "cellar": "Sklep",
        "priceNote": "Poznámka k ceně",
        "location": "Umístění objektu",
        "floor": "Podlaží",
        "building": "Stavba",
        "buildingCondition": "Stav objektu",
        "lift": "Výtah",
        "ownership": "Vlastnictví",
        "id": "ID zakázky",
        "idOrder": "ID",
        "energyPerformanceOfBuilding": "Energetická náročnost budovy",
        "barrieFree": "Bezbariérový",
        "parking": "Parkování",
        "garage": "Garáž",
        "equipped": "Vybavení",
        "transferToPersonalOwnership": "Převod do OV",
        "yearOfApproval": "Rok kolaudace"
    }

    for key, value in dict_detailsAttr_binding.items():
        try:
            dict_offerDetailsAttr[key] = dict_detailsTableOfOffer[value]
        except KeyError:
            logging.warning(key + " was not grabbed.", exc_info=True)

    # Parsing specifically saved attribues
    dict_specific_detailsAttr_binding = {
        "transport": "Doprava",
        "water": "Voda",
        "gas": "Plyn",
        "heating": "Topení",
        "waste": "Odpad",
        "electricity": "Elektřina",
        "roads": "Komunikace"
    }

    for key, value in dict_specific_detailsAttr_binding.items():
        try:
            dict_offerDetailsAttr[key] = dict_detailsTableOfOffer[value][0]["value"]
        except KeyError:
            logging.warning(key + " was not grabbed.", exc_info=True)

    # Parsing of distances from json object
    dict_poi = {}
    try:
        dist = data["poi"]
        dict_poi = actions.convertToKeyValue(dist, "name", "distance", True)
    except KeyError:
        logging.info("Offer does not contains POI data.")

    dict_distance_binding = {
        "playgroundDistance": "Hřiště",
        "culturalHeritageDistance": "Kulturní památka",
        "publicTransportDistance": "Bus MHD",
        "sportsGroundDistance": "Sportoviště",
        "tramDistance": "Tram",
        "metroDistance": "Metro",
        "trainDistance": "Vlak",
        "sweetshopDistance": "Cukrárna",
        "cinemaDistance": "Kino",
        "convenienceStoreDistance": "Večerka",
        "pubDistance": "Hospoda",
        "theaterDistance": "Divadlo",
        "veterinaryDistance": "Veterinář",
        "restaurantDistance": "Restaurace",
        "schoolDistance": "Škola",
        "postOfficeDistance": "Pošta",
        "storeDistance": "Obchod",
        "pharmacyDistance": "Lékárna",
        "atmDistance": "Bankomat",
        "doctorDistance": "Lékař",
        "preSchoolDistance": "Školka",
        "naturalAttractionDistance": "Přírodní zajímavost"
    }

    # for each distance attributes add them to final dict
    for key, value in dict_distance_binding.items():
        try:
            dict_offerDetailsAttr[key] = dict_poi[value]
        except KeyError:
            logging.warning(key + " was not grabbed.", exc_info=True)
        except NameError:
            logging.info("Missing values in offer.", exc_info=True)
            continue

    # replace None with NA to prevent skipping columns
    for key, value in dict_offerDetailsAttr.items():
        if value is None:
            dict_offerDetailsAttr[key] = "NA"
        else:
            continue
    # print(dict_offerDetailsAttr)
    list_onlyValues = list(dict_offerDetailsAttr.values())

    # oAuth 2.0 Google
    creds = None

    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'C:\\Users\\pavel\\Disk Google\\finance\\nemovitosti\\nemovitostiSecretOauth.json', SCOPES)
            creds = flow.run_local_server(port=8000)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = discovery.build('sheets', 'v4', credentials=creds)

    # The ID of the spreadsheet to update.
    spreadsheet_id = '1YPWOsBVm2qGOWJx4dgniopZ_Ekm91h7hxy2-enof7N8'

    # Values will be appended after the last row of the table.
    range_ = 'A1:BL2'

    # How the input data should be interpreted.
    value_input_option = 'RAW'

    # How the input data should be inserted.
    insert_data_option = 'INSERT_ROWS'

    value_range_body = {"values": [list_onlyValues], "range": "A1:BL2"}

    request = service.spreadsheets().values().append(spreadsheetId=spreadsheet_id, range=range_,
                                                     valueInputOption=value_input_option,
                                                     insertDataOption=insert_data_option, body=value_range_body)
    response = request.execute()
    # pprint(response)