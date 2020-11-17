import actions


def execute(url):
    # get list of offer at page and html of page
    listOfOffers, html = actions.scrapeListOfOffers(url)

    # check if there is next page
    nextPage, newUrl = actions.checkNextPageOccurance(html)

    return listOfOffers, nextPage, newUrl
