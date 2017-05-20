import requests
import json
import re
from lxml import html
import nba.ops.mlDataPrep as ml
import nba.ops.driverWaits as waits 
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from nba.classes.NbaPlayerStat import NbaPlayerStat
from nba.ops.config import APP_CONFIG
import nba.ops.jsonData as jsonData

config = APP_CONFIG

def getTournamentAverageScores():

    driver = webdriver.PhantomJS()
    driver.set_window_size(1124, 850)

    baseUrl = "https://www.fantasycruncher.com/lineup-rewind/fanduel/NBA/"
    dates = ml.getDateRangeArr('2017-03-15', '2017-04-12')
    rowsSelector = "#tournament-links-table-container"
    # tournamentTypes = ["Double Up", "Triple Up", "Quintuple Up"]
    bigTerm = "BIG"

    cutoffs = {}

    for date in dates:
        fullUrl = baseUrl + date

        cutoffsForDate = {
            "Double Up": [],
            "Double Up BIG": [],
            "Triple Up": [],
            "Triple Up BIG": [],
            "Quintuple Up": [],
            "Quintuple Up BIG": []
        }

        try:
            driver.get(fullUrl)
            print("Getting..", date)

            closeLogin = waits.byClass('close-login-alert', driver)
            closeLogin.click()

            openTab = waits.byClass("open-tournament-links", driver)
            openTab.click()

            tableCont = waits.byId("tournament-links-table-container", driver)

            rawHtml = driver.page_source

            tableRowsSelector = 'table.tournament-links-table tbody tr'

            tree = html.fromstring(rawHtml)
            rows = tree.cssselect(tableRowsSelector)

            for row in rows:
                tournamentName = row[0].text_content()
                if "Double Up" in tournamentName and bigTerm not in tournamentName:
                    cutoffsForDate["Double Up"].append(float(row[8].text_content()))
                elif "Double Up" in tournamentName and bigTerm in tournamentName:
                    cutoffsForDate["Double Up BIG"].append(float(row[8].text_content()))
                elif "Triple Up" in tournamentName and bigTerm not in tournamentName:
                    cutoffsForDate["Triple Up"].append(float(row[8].text_content()))
                elif "Triple Up" in tournamentName and bigTerm in tournamentName:
                    cutoffsForDate["Triple Up BIG"].append(float(row[8].text_content()))
                elif "Quintuple Up" in tournamentName and bigTerm not in tournamentName:
                    cutoffsForDate["Quintuple Up"].append(float(row[8].text_content()))
                elif "Quintuple Up" in tournamentName and bigTerm in tournamentName:
                    cutoffsForDate["Quintuple Up BIG"].append(float(row[8].text_content()))

        except Exception as e:
            continue

        cutoffs[date] = {}
        for tournamentType, cutoffArr in cutoffsForDate.items():
            try:
                average = sum(cutoffArr) / float(len(cutoffArr))
            except ZeroDivisionError as e:
                average = None

            cutoffs[date][tournamentType] = average

    filename = jsonData.LOCAL_DATA_PATH + "2017_tournament_results.json"
    with open(filename, 'w') as fp:
        json.dump(cutoffs, fp)

    driver.quit()

    return "DONE"

allCutoffs = getTournamentAverageScores()
print(allCutoffs)
# for key, cutoffs in allCutoffs.items():
#     if len(cutoffs) > 0:
#         print(key, "NUMBER:", len(cutoffs), "AVERAGE:", sum(cutoffs) / float(len(cutoffs)))
#     else:
#         print("NO TOURNAMENTS FOR", key)



