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

config = APP_CONFIG

def getTournamentAverageScores():

    driver = webdriver.PhantomJS()
    driver.set_window_size(1124, 850)

    baseUrl = "https://www.fantasycruncher.com/lineup-rewind/fanduel/NBA/"
    dates = ml.getDateRangeArr('2016-10-25', '2017-03-27')
    rowsSelector = "#tournament-links-table-container"
    # tournamentTypes = ["Double Up", "Triple Up", "Quintuple Up"]
    bigTerm = "BIG"

    cutoffArrs = {
        "Double Up": [],
        "Double Up BIG": [],
        "Triple Up": [],
        "Triple Up BIG": [],
        "Quintuple Up": [],
        "Quintuple Up BIG": []
    }

    for date in dates:
        fullUrl = baseUrl + date
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
                    cutoffArrs["Double Up"].append(float(row[8].text_content()))
                elif "Double Up" in tournamentName and bigTerm in tournamentName:
                    cutoffArrs["Double Up BIG"].append(float(row[8].text_content()))
                elif "Triple Up" in tournamentName and bigTerm not in tournamentName:
                    cutoffArrs["Triple Up"].append(float(row[8].text_content()))
                elif "Triple Up" in tournamentName and bigTerm in tournamentName:
                    cutoffArrs["Triple Up BIG"].append(float(row[8].text_content()))
                elif "Quintuple Up" in tournamentName and bigTerm not in tournamentName:
                    cutoffArrs["Quintuple Up"].append(float(row[8].text_content()))
                elif "Quintuple Up" in tournamentName and bigTerm in tournamentName:
                    cutoffArrs["Quintuple Up BIG"].append(float(row[8].text_content()))

        except Exception as e:
            continue
        # break

    driver.quit()

    return cutoffArrs

allCutoffs = getTournamentAverageScores()
for key, cutoffs in allCutoffs.items():
    if len(cutoffs) > 0:
        print(key, "NUMBER:", len(cutoffs), "AVERAGE:", sum(cutoffs) / float(len(cutoffs)))
    else:
        print("NO TOURNAMENTS FOR", key)



