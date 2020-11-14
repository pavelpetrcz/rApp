import actions


def execute():
    startingPointUrl = "https://www.sreality.cz/hledani/prodej/byty"

    # get list of offer at page and html of page
    listOfOffers, html = actions.scrapeListOfOffers(startingPointUrl)

    # check if there is next page
    nextPage = actions.checkNextPageOccurance(html)

    return listOfOffers, nextPage
