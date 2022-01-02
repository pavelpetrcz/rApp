#  Copyright (c) Pavel Petr 2021.


import time
import logging
import os
import schedule

import actions

if __name__ == "__main__":
    # constants
    again = True
    collection_name = ""

    # logging setup
    logging.basicConfig(
        filename='app.log',
        filemode='w',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # establish db connection
    try:
        conn_string = 'mongodb+srv://ppetr:{}@clusterppe.hga2z.mongodb.net/estates?retryWrites=true&w=majority'.format(
            os.environ['db_pass'])
        clientDb = actions.getDbConn(connection_string=conn_string)
        collection_name = clientDb["flats"]
    except Exception as e:
        logging.error(e, stack_info=True, exc_info=True)

    # scrape content every 24 hours
    try:
        schedule.every(24).hours.do(actions.scrapeContent, collection_name=collection_name)
    except Exception as exc:
        logging.warning(exc, stack_info=True, exc_info=True)

    # run schedule
    while again:
        schedule.run_pending()
        time.sleep(1)
