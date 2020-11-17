import math
import requests
import time

from selenium import webdriver
from bs4 import BeautifulSoup


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
        dict_result[key] = value
        if roundDown:
            rvalue = math.floor(value)
            dict_result[key] = rvalue

    return dict_result


def getOfferJson(partOfUrl):
    """
    :param partOfUrl: id of offer parsed from HTML
    :return: complet JSON of offer
    """
    url = "https://www.sreality.cz/api/cs/v2/estates/"

    final_url = url + partOfUrl
    time.sleep(1)
    response = requests.get(final_url)
    result = response.json()
    return result


def scrapeListOfOffers(url):
    """
    :param: url where to scrape urls of offers
    :return: list of offer URLs at page
    """

    # base Url
    baseUrl = "https://www.sreality.cz"

    scrapeAgain = True
    scrapeSleep = 2
    itemsPerPage = 0
    soupHtml = ""

    while scrapeAgain:
        soupHtml = getHTML(url, scrapeSleep)

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
        href = "href"
        parseUrlOfOfferDetail = soupHtml.findAll("a", {"class": "title"})[a]["href"]
        detailUrl = baseUrl + parseUrlOfOfferDetail
        listOfUrls.append(detailUrl)
        a = a + 1

    # concatate url for next scrape
    return listOfUrls, soupHtml


def getHTML(url, sec):
    """
    :param url: address of page to scrape
    :param sec: number of sec to wait between requests (i.e. 1)
    :return: HTML of page
    """
    # open chrome
    browser = webdriver.Chrome()

    # open URL
    browser.get(url)
    time.sleep(sec)

    # download page in HTML
    html = browser.page_source

    # close chrome
    browser.close()

    # parse html with BS
    soupHtml = BeautifulSoup(html, "html.parser")
    return soupHtml


def checkNextPageOccurance(sourceCode):
    if sourceCode.findAll("a", {"class": "btn-paging-pn icof icon-arr-right paging-next"}):
        exists = True
        newUrl = sourceCode.findAll("a", {"class": "btn-paging-pn icof icon-arr-right paging-next"})[0]["href"]
    else:
        exists = False

    return exists, newUrl
