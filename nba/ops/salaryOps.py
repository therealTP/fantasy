import requests
import json
from selenium import webdriver

import nba.scrapers.rotowire_scraper as rw
import nba.scrapers.fc_scraper as fc

import nba.ops.mlDataPrep as ml
import nba.ops.logger as logger
import nba.ops.apiCalls as api 

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
        'allNewIds': []
    }

    for date in dateArr:
        salariesForDate = fc.getSalaryDataForDate(date, site, playerData, driver)
        allData['allSalaries'].extend(salariesForDate['currentPlayerSalaries'])
        allData['allNewIds'].extend(salariesForDate['missingPlayerIds'])

    newSalariesResponse = api.postSalaries(allData['allSalaries'])
    # UNCOMMENT LINE BELOW IF ALSO WANT TO ADD NEW FC IDS
    # newIdsResponse = api.postNewIds(allData['allNewIds'])
    
    return "DONE"

# salaryDates = ml.getDateRangeArr('2015-11-04', '2016-04-13')
# getSalariesForDatesAndPostToApi(salaryDates)


        