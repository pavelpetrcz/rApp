import actions


def execute(listOfOffers):

    jsonDataHolder = []

    for item in listOfOffers:
        splittedItem = item.split("/")
        jsonData = actions.getOfferJson(splittedItem[-1])
        jsonDataHolder.append(jsonData)

    return jsonDataHolder
