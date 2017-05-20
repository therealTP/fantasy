import requests
import json

import nba.ops.logger as logger
import nba.scrapers.rotowire_scraper as rw
import nba.scrapers.game_lines_scraper as lines
import nba.ops.apiCalls as api
import nba.ops.csvOps as csvOps
import nba.ops.jsonData as jsonData

def getSpreadsForTodayAndPostToApi():
    # this fcn uses RW to get today's games spreads
    session = requests.Session()
    rawSpreadHtml = rw.getRawHtmlForSpreads(session)
    games = api.getTodaysGames()
    spreads = rw.extractSpreads(rawSpreadHtml, games)

    spreadResponse = api.postGameSpreads(spreads)

    # log task
    # logger.logSpreadScrapeTaskSuccess(spreads)

    # return len(spreads)

def get_spreads_for_months_and_write_to_csv():
    # this fcn uses oddsshark to scrape past game lines

    all_line_data = lines.scrapeLineData()
    parsed_line_data = lines.parseLineData(all_line_data)
    final_data = lines.finalizeLineData(parsed_line_data)
    folder = jsonData.LOCAL_DATA_PATH
    filename = folder + 'game-line-data.csv'
    csvOps.writeToCsv(final_data, filename)

get_spreads_for_months_and_write_to_csv()