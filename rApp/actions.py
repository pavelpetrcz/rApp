# -*- coding: utf-8 -*-
"""
Created on Sat Oct 17 19:26:21 2020

@author: pavel
"""
from __future__ import print_function
import requests
import re
import uuid
import time
import string
import gspread
import pandas as pd
import pickle
import os.path
import logging

from datetime import datetime, timezone
from dateutil.parser import parse
from bs4 import BeautifulSoup
from time import sleep
from selenium import webdriver
from oauth2client.service_account import ServiceAccountCredentials
from df2gspread import gspread2df as g2d
from df2gspread import df2gspread as d2g
from pprint import pprint
from googleapiclient import discovery


from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


def scrapeListOfOffers():
    startingPointUrl = "https://www.sreality.cz/hledani/prodej/byty"

    # base Url
    baseUrl = "https://www.sreality.cz"

    scrapeAgain = True
    scrapeSleep = 2

    while (scrapeAgain):
        # open chrome
        browser = webdriver.Chrome()
    
        # open URL
        browser.get(startingPointUrl)
    
        # download page in HTML
        html = browser.page_source
        time.sleep(scrapeSleep)
    
        # close chrome
        browser.close()
    
        # parse html with BS
        soupHtml = BeautifulSoup(html, "html.parser")
        
        # count of item in scraped page
        itemsPerPage = len(soupHtml.findAll("a", {"class": "title"}))
        
        #if scraping was not successful do it again slower
        if (itemsPerPage == 0):
            scrapeAgain = True
            scrapeSleep += 1
        else:
            scrapeAgain = False
    
    #parsed URLs of all offer at page
    a = 0
    listOfUrls = []

    while (a < itemsPerPage):
        parseUrlOfOfferDetail = soupHtml.findAll("a", {"class": "title"})[a]["href"]
        detailUrl = baseUrl + parseUrlOfOfferDetail
        listOfUrls.append(detailUrl)
        a = a + 1
    
    #concateta url for next scrape
    
    return listOfUrls


# method to scrape one offer page

def scrapeOffer(detailUrl):
    # dict pro všechny informace z nabídky
    list_offerDetailsAttr = ["internalId", "idOrder", "id", "offerName", "address", "offeredPrice", "offeredPriceException", "priceNote", "desc", "utilitiesCosts", "yearOfReconstruction", "offerUpdatedDate", "floor", "ownership", "transferToPersonalOwnership", "location", "locationDesc", "usableArea", "balconySqMeter", "terraceSqMeter", "cellarSqMeter", "yearOfApproval", "water", "gas", "heating", "waste", "connectivity", "buildingCondition", "building", "electricity", "transport", "roads", "energyPerformanceOfBuilding", "barrieFree", "terrace", "garage", "cellar", "equipped", "parking", "loggia", "lift", "sweetshopDistance", "cinemaDistance", "playgroundDistance", "culturalHeritageDistance", "naturalAttractionDistance", "convenienceStoreDistance", "pubDistance", "theaterDistance", "veterinaryDistance", "publicTransportDistance", "sportsGroundDistance", "tramDistance", "trainDistance", "restaurantDistance", "metroDistance", "storeDistance", "schoolDistance", "doctorDistance", "atmDistance", "preSchoolDistance", "schoolDistance", "pharmacyDistance", "trainDistance", "postOfficeDistance"]
    dict_offerDetailsAttr = dict.fromkeys(list_offerDetailsAttr)

    # open page with offer
    browser = webdriver.Chrome()
    browser.get(detailUrl)
    detailOfferHtml = browser.page_source
    time.sleep(2)
    browser.close()
    soupDetailOfferHtml = BeautifulSoup(detailOfferHtml, "html.parser")
    
    
    #generate unique random id in hexadecimal
    g = uuid.uuid4().hex
    
    
    # set as internal id
    dict_offerDetailsAttr["internalId"] = g
    
    # Parsing offer name
    try:
        s_offerName = soupDetailOfferHtml.find("span", {"itemprop": "name"}).find("span", {"class": "name ng-binding"}).get_text()
        dict_offerDetailsAttr["offerName"] = s_offerName
    except:
        logging.warning(soupDetailOfferHtml)
        pass
    
    try:
        # __Parsing address__
        s_address = soupDetailOfferHtml.find("span", {"itemprop": "name"}).find("span", {"class": "location-text ng-binding"}).get_text()
        dict_offerDetailsAttr["address"] = s_address
    except:
        logging.warning(soupDetailOfferHtml)
        pass
    
    # parse string with price
    try:
        s_offeredPrice = soupDetailOfferHtml.find("span", {"ng-if": "contentData.price"}).find("span", {"class": "norm-price ng-binding"}).get_text()
        #constant with specific info
        check = "Info o ceně u RK"
    
        #if price is not number, save text, if it is real price parse just number
        if (s_offeredPrice != check):
            res = re.sub(r'\D', "", s_offeredPrice)
            dict_offerDetailsAttr["offeredPrice"] = res
        else:
            dict_offerDetailsAttr["offeredPriceException"] = "infoRk"
    except:
        logging.warning(soupDetailOfferHtml)
        pass
    
    # __Parsing description__
    
    s_desc = soupDetailOfferHtml.find("div", {"itemprop": "description"}).get_text()
    dict_offerDetailsAttr["desc"] = s_desc
    
    
    # __Parsing additional data from table below description__
    #find all labels
    li_tags = soupDetailOfferHtml.findAll("li")
    
    # all of lables strip from whitespaces and remove "None" and place to list
    list_table_of_att = [] 
    for item in li_tags:
        a = item.get_text().strip().replace("\n", "")
        list_table_of_att.append(a)
    list_table_of_att = list(filter(None, list_table_of_att))
    
    dict_table_of_att = {}
    rounds = len(list_table_of_att)
    
    #for earch item in dict go throught and set key and value
    for item in range(rounds):
        #split value by ":"
        list_label_value = list_table_of_att[item].split(":")
        #count lenght of list
        length = len(list_label_value)
        # if list contains 2 items (key:value) then set ..
        if (length == 2):
            #if it is value about distance then separate number and set in new dict
            if (re.search('\(\d{1,5}', list_label_value[1])):
                r = re.findall('\d{1,5}', list_label_value[1])
                xset = r[0]
            #if after split contains list only one item ten set it as key and add "nic" as value
            else:
                xset = list_label_value[1]
            #set new key:value in new list
            dict_table_of_att[list_label_value[0]] = xset
        else:
            dict_table_of_att[list_label_value[0]] = "nic"
        
    dict_table_of_att
    
    # list of span tags with specific class attr
    bool_values = soupDetailOfferHtml.findAll("span", {"class": "icof"})
    #regexes for testing
    reg_ok = "boolean-true"
    reg_nok = "boolean-false"
    
    
    list_bool_values = []
    
    # for each line of html with span tag test if contains regex and according to value append True or False to list above
    for item in bool_values:
        if (re.findall(reg_ok, str(item))):
            list_bool_values.append(True)
        elif (re.findall(reg_nok, str(item))):
            list_bool_values.append(False)
        else:
            continue
    
    order = 0
    # for each item in dict where is no values we set bool value according to scrape data above
    for item in dict_table_of_att:
        if (dict_table_of_att[item]) == "":
            dict_table_of_att[item] = list_bool_values[order]
            order += order
    
    
    dict_table_of_att
    
    
    # __Parsing last date and time updated__
    
    #set now
    time_now = datetime.fromtimestamp(time.time())
    
    # if offer was updated today, they state "today" instead of date therefore ...
    if dict_table_of_att['Aktualizace'] == "Dnes":
        dict_offerDetailsAttr['offerUpdatedDate'] = time_now.strftime("%d/%m/%Y")
    
        #if update is date, we use that formatted date
    else: 
        dtime = parse(str(dict_table_of_att['Aktualizace']))
        dict_offerDetailsAttr['offerUpdatedDate'] = dtime.strftime("%d/%m/%Y")
    
    
    # __Parsing of usable area, terrace and cellar__
    try:
        list_a = dict_table_of_att['Užitná plocha'].split("m")
        dict_offerDetailsAttr['usableArea'] = list_a[0]
    except:
        pass
    try:
        list_b = dict_table_of_att['Terasa'].split("m")
        dict_offerDetailsAttr['terraceSqMeter'] = list_b[0]
    except:
        pass
    try:
        list_b = dict_table_of_att['Sklep'].split("m")
        dict_offerDetailsAttr['cellarSqMeter'] = list_b[0]
    except:
        pass
    
    # __Parsing of priceNote, location, floor, buildingCondition, building, lift, ownership, ID, water, heating, waste, gas, electricity__
    try:
        dict_offerDetailsAttr['priceNote'] = dict_table_of_att['Poznámka k ceně']
    except:
        pass
    try:
        dict_offerDetailsAttr['location'] = dict_table_of_att['Umístění objektu']
    except:
        pass
    try:
        dict_offerDetailsAttr['floor'] = dict_table_of_att['Podlaží']
    except:
        pass
    try:
        dict_offerDetailsAttr['building'] = dict_table_of_att['Stavba']
    except:
        pass
    try:
        dict_offerDetailsAttr['buildingCondition'] = dict_table_of_att['Stav objektu']
    except:
        pass
    try:
        dict_offerDetailsAttr['lift'] = dict_table_of_att['Výtah']
    except:
        pass
    try:
        dict_offerDetailsAttr['ownership'] = dict_table_of_att['Vlastnictví']
    except:
        pass
    try:
        dict_offerDetailsAttr["id"] = dict_table_of_att['ID zakázky']
    except:
        pass
    try:
        dict_offerDetailsAttr["idOrder"] = dict_table_of_att['ID']
    except:
        pass
    try:
        dict_offerDetailsAttr['energyPerformanceOfBuilding'] = dict_table_of_att['Energetická náročnost budovy']
    except:
        pass
    try:
        dict_offerDetailsAttr['water'] = dict_table_of_att['Voda']
    except:
        pass
    try:
        dict_offerDetailsAttr['gas'] = dict_table_of_att['Plyn']
    except:
        pass
    try:
        dict_offerDetailsAttr['heating'] = dict_table_of_att['Topení']
    except:
        pass
    try:
        dict_offerDetailsAttr['waste'] = dict_table_of_att['Odpad']
    except:
        pass
    try:
        dict_offerDetailsAttr['electricity'] = dict_table_of_att['Elektřina']
    except:
        pass
    try:
        dict_offerDetailsAttr['heating'] = dict_table_of_att['Topení']
    except:
        pass
    try:
        dict_offerDetailsAttr['connectivity'] = dict_table_of_att['Telekomunikace']
    except:
        pass
    try:
        dict_offerDetailsAttr['transport'] = dict_table_of_att['Doprava']
    except:
        pass
    try:
        dict_offerDetailsAttr['roads'] = dict_table_of_att['Komunikace']
    except:
        pass
    try:
        dict_offerDetailsAttr['barrieFree'] = dict_table_of_att['Bezbariérový']
    except:
        pass
    try:
        dict_offerDetailsAttr['lift'] = dict_table_of_att['Výtah']
    except:
        pass
    try:
        dict_offerDetailsAttr['parking'] = dict_table_of_att['Parkování']
    except:
        pass
    try:
        dict_offerDetailsAttr['terrace'] = dict_table_of_att['Terasa']
    except:
        pass
    try:
        dict_offerDetailsAttr['cellar'] = dict_table_of_att['Sklep']
    except:
        pass
    try:
        dict_offerDetailsAttr['garage'] = dict_table_of_att['Garáž']
    except:
        pass
    try:
        dict_offerDetailsAttr['equipped'] = dict_table_of_att['Vybavení']
    except:
        pass
    try:
        dict_offerDetailsAttr['transferToPersonalOwnership'] = dict_table_of_att['Převod do OV']
    except:
        pass
    try:
        dict_offerDetailsAttr['yearOfApproval'] = dict_table_of_att['Rok kolaudace']
    except:
        pass
    
    # __Parsing of distances__
    try:
        dict_offerDetailsAttr['playgroundDistance'] = dict_table_of_att['Hřiště']
    except:
        pass
    try:
        dict_offerDetailsAttr['culturalHeritageDistance'] = dict_table_of_att['Kulturní památka']
    except:
        pass
    try:
        dict_offerDetailsAttr['publicTransportDistance'] = dict_table_of_att['Bus MHD']
    except:
        pass
    try:
        dict_offerDetailsAttr['sportsGroundDistance'] = dict_table_of_att['Sportoviště']
    except:
        pass
    try:
        dict_offerDetailsAttr['tramDistance'] = dict_table_of_att['Tram']
    except:
        pass
    try:
        dict_offerDetailsAttr['metroDistance'] = dict_table_of_att['Metro']
    except:
        pass
    try:
        dict_offerDetailsAttr['trainDistance'] = dict_table_of_att['Vlak']
    except:
        pass
    try:
        dict_offerDetailsAttr['sweetshopDistance'] = dict_table_of_att['Cukrárna']
    except:
        pass
    try:
        dict_offerDetailsAttr['cinemaDistance'] = dict_table_of_att['Kino']
    except:
        pass
    try:
        dict_offerDetailsAttr['convenienceStoreDistance'] = dict_table_of_att['Večerka']
    except:
        pass
    try:
        dict_offerDetailsAttr['pubDistance'] = dict_table_of_att['Hospoda']
    except:
        pass
    try:
        dict_offerDetailsAttr['theaterDistance'] = dict_table_of_att['Divadlo']
    except:
        pass
    try:
        dict_offerDetailsAttr['veterinaryDistance'] = dict_table_of_att['Veterinář']
    except:
        pass
    try:
        dict_offerDetailsAttr['restaurantDistance'] = dict_table_of_att['Restaurace']
    except:
        pass
    try:
        dict_offerDetailsAttr['schoolDistance'] = dict_table_of_att['Škola']
    except:
        pass
    try:
        dict_offerDetailsAttr['postOfficeDistance'] = dict_table_of_att['Pošta']
    except:
        pass
    try:
        dict_offerDetailsAttr['storeDistance'] = dict_table_of_att['Obchod']
    except:
        pass
    try:
        dict_offerDetailsAttr['trainDistance'] = dict_table_of_att['Vlak']
    except:
        pass
    try:
        dict_offerDetailsAttr['pharmacyDistance'] = dict_table_of_att['Lékárna']
    except:
        pass
    try:
        dict_offerDetailsAttr['atmDistance'] = dict_table_of_att['Bankomat']
    except:
        pass
    try:
        dict_offerDetailsAttr['doctorDistance'] = dict_table_of_att['Lékař']
    except:
        pass
    try:
        dict_offerDetailsAttr['preSchoolDistance'] = dict_table_of_att['Školka']
    except:
        pass
    try:
        dict_offerDetailsAttr['naturalAttractionDistance'] = dict_table_of_att['Přírodní zajímavost']
    except:
        pass
    
    
    
    # TODO: Change placeholder below to generate authentication credentials. See
    # https://developers.google.com/sheets/quickstart/python#step_3_set_up_the_sample
    #
    # Authorize using one of the following scopes:
    #     'https://www.googleapis.com/auth/drive'
    #     'https://www.googleapis.com/auth/drive.file'
    #     'https://www.googleapis.com/auth/spreadsheets'
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
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    
    service = discovery.build('sheets', 'v4', credentials=creds)
    
    # The ID of the spreadsheet to update.
    spreadsheet_id = '1YPWOsBVm2qGOWJx4dgniopZ_Ekm91h7hxy2-enof7N8'  
    
    # Values will be appended after the last row of the table.
    range_ = 'A2:BL2'
    
    # How the input data should be interpreted.
    value_input_option = 'RAW'
    
    # How the input data should be inserted.
    insert_data_option = 'INSERT_ROWS'
    
    value_range_body = {"values": [["a", "b"]], "range": "A1:B1"}
    
    request = service.spreadsheets().values().append(spreadsheetId=spreadsheet_id, range=range_, valueInputOption=value_input_option, insertDataOption=insert_data_option, body=value_range_body)
    response = request.execute()
    
    # TODO: Change code below to process the `response` dict:
    pprint(response)
    
    # ## Save to spreadsheet
    # udf = pd.DataFrame.from_dict(dict_offerDetailsAttr, orient='index')
    # udf_transpose = udf.transpose()
    
    # # accessing Google Spreadsheet
    # scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    # creds = ServiceAccountCredentials.from_json_keyfile_name('C:\\Users\\pavel\\Disk Google\\finance\\nemovitosti\\nemovitostiSecret.json', scope)
    # client = gspread.authorize(creds)
    
    # # opening specific spreadsheet
    # sheet = client.open('srealityOffers').sheet1
    
    # # sheet name
    # wks_name = 'data'
    
    # # prepare cell where to start saving
    # st = "A" + str(startline)
    
    # # upload final dataframe with new column to G-sheet
    # d2g.upload(udf_transpose, spreadsheet_key, wks_name, credentials=creds, row_names=True, start_cell=st)
    print("offerSaved")