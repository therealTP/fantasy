import requests
import json
from selenium import webdriver

import nba.scrapers.rotowire_scraper as rw
import nba.scrapers.fc_scraper as fc

import nba.ops.mlDataPrep as ml
import nba.ops.csvOps as csvOps
import nba.ops.logger as logger
import nba.ops.apiCalls as api
import nba.ops.jsonData as jsonData

# this fcn used for automated task
def getSalariesForTodayAndPostToApi():
    session = requests.Session()
    rawSalaryHtml = rw.getRawHtmlForSalaries(session)
    players = api.getCurrentPlayerData()
    salaryData = rw.extractSalaries(rawSalaryHtml, players)

    salaries = salaryData["currentPlayerSalaries"]
    newPlayerIds = salaryData["newPlayerIds"]

    # print(salaries)

    salaryResponse = api.postSalaries(salaries)
    newIdsResponse = api.postNewIds(newPlayerIds)

    # log task
    logger.logSalaryScrapeTaskSuccess(salaries)

    return len(salaries)

# this fcn used for manual bulk scraping
def getSalariesForDatesAndPostToApi(dateArr, site):
    '''
    :param dateArr: array of YYYY-MM-DD date strings
    :param site: 'fanduel' or 'draftkings'
    :return: all new salaries & new ids in dict
    '''
    driver = webdriver.PhantomJS()
    driver.set_window_size(1124, 850)

    playerData = api.getCurrentPlayerData()

    allData = {
        'allSalaries': [],
        'allNewIds': []
    }

    # for each date in range:
    for date in dateArr:
        # get salary & pos data
        salariesForDate = fc.getSalaryDataForDate(date, site, playerData, driver)

        # add salary & missing player data
        allData['allSalaries'].extend(salariesForDate['currentPlayerSalaries'])
        allData['allNewIds'].extend(salariesForDate['missingPlayerIds'])

    newSalariesResponse = api.postSalaries(allData['allSalaries'])
    # UNCOMMENT LINE BELOW IF ALSO WANT TO ADD NEW FC IDS
    # dedupedNewIds = [i for n, i in enumerate(allData["allNewIds"]) if i not in allData["allNewIds"][n + 1:]]
    # newIdsResponse = api.postNewIds(dedupedNewIds)
    
    return allData

salaryDates = ml.getDateRangeArr('2017-03-15', '2017-04-12')
allUpdates = getSalariesForDatesAndPostToApi(salaryDates, "fanduel")

# INCOMPLETE: this fcn used for manual bulk scraping of position changes
def getPositionChangesForDatesAndWriteToCsv(dateArr):
    driver = webdriver.PhantomJS()
    driver.set_window_size(1124, 850)

    playerData = api.getCurrentPlayerData()

    site = "fanduel"  # fanduel or draftkings?

    allData = {
        'allPositionUpdates': []
    }

    # keeps track of dupes
    allPosChanges = []

    # for each date in range:
    for date in dateArr:
        # get salary & pos data
        salariesForDate = fc.getSalaryDataForDate(date, site, playerData, driver)

        # for all new positions for date:
        for newPos in salariesForDate['playerPositionUpdates']:

            # if new pos change has already been added:
            if newPos in allPosChanges:
                continue
            # if not, add to changes & record
            else:
                # keep track of pos changes already logged
                allPosChanges.append(newPos)
                # create row for csv storing
                fullChangeRow = [newPos["playerId"], date, newPos["newPosition"]]
                allData["allPositionUpdates"].append(fullChangeRow)

    # posUpdates = sorted(allData['allPositionUpdates'], key=lambda k: k['playerId'])
    # print(allData["allPositionUpdates"])
    # print(posUpdates)
    # posUpdatesResponse = api.updatePlayerPositions(posUpdates)
    # csvOps.writeToCsv(allUpdates["allPositionUpdates"], fileLoc

    return allData


