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
def getSalariesForDatesAndPostToApi(dateArr):
    driver = webdriver.PhantomJS()
    driver.set_window_size(1124, 850)

    playerData = api.getCurrentPlayerData()
    
    site = "fanduel" #fanduel or draftkings?

    allData = {
        'allSalaries': [],
        'allNewIds': [],
        'allPositionUpdates': []
    }

    allPosChanges = []

    # for each date in range:
    for date in dateArr:
        # get salary & pos data
        salariesForDate = fc.getSalaryDataForDate(date, site, playerData, driver)

        # add salary & missing player data
        allData['allSalaries'].extend(salariesForDate['currentPlayerSalaries'])
        allData['allNewIds'].extend(salariesForDate['missingPlayerIds'])
        
        # for all new positions for date:
        for newPos in salariesForDate['playerPositionUpdates']:
            
            # if new pos change has already been added:
            if newPos in allPosChanges:
                continue
            # if not, add to changes & record 
            else:
                # keep track of pos changes already logged
                allPosChanges.append(newPos)
                fullChangeRow = [newPos["playerId"], date, newPos["newPosition"]]
                # fullChangeRow = {
                #     "playerId": newPos["playerId"], 
                #     "newPosition": newPos["newPosition"]
                # }

                allData["allPositionUpdates"].append(fullChangeRow)

            # if newPos not in allData['allPositionUpdates']:
            #     allData['allPositionUpdates'].append(newPos)
                # if playerId has already been recorded w/ diff pos change:
                # if newPos["playerId"] in newPosPlayers:
                #     print("MULTIPLE POS CHANGE PLAYER", newPos["playerId"])
                # else:
                #     # first time player/pos combo added, will add playerId
                #     newPosPlayers.append(newPos["playerId"])

    # posUpdates = sorted(allData['allPositionUpdates'], key=lambda k: k['playerId'])
    # print(allData["allPositionUpdates"])
    # print(posUpdates)
    # posUpdatesResponse = api.updatePlayerPositions(posUpdates)

    # newSalariesResponse = api.postSalaries(allData['allSalaries'])
    # UNCOMMENT LINE BELOW IF ALSO WANT TO ADD NEW FC IDS
    # newIdsResponse = api.postNewIds(allData['allNewIds'])
    
    return allData

filename = "missing_pos_data_2017_final.csv"
fileLoc = jsonData.LOCAL_DATA_PATH + filename 

salaryDates = ml.getDateRangeArr('2017-03-27', '2017-04-12')
allUpdates = getSalariesForDatesAndPostToApi(salaryDates)
# print(allUpdates["allPositionUpdates"])
csvOps.writeToCsv(allUpdates["allPositionUpdates"], fileLoc)


        