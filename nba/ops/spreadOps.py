import requests
import json

import nba.ops.logger as logger
import nba.scrapers.rotowire_scraper as rw
import nba.ops.apiCalls as api 

def getSpreadsForTodayAndPostToApi():
    session = requests.Session()
    rawSpreadHtml = rw.getRawHtmlForSpreads(session)
    games = api.getTodaysGames()
    spreads = rw.extractSpreads(rawSpreadHtml, games)

    spreadResponse = api.postGameSpreads(spreads)

    # log task
    # logger.logSpreadScrapeTaskSuccess(spreads)

    # return len(spreads)
        