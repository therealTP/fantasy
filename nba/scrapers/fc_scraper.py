####
# NOTE: This scraper can only get salaries for >= 2 days in the past, as site does not update in real time
# For real time, day-of salaires
####
import requests
import json
import os
from lxml import html
import nba.ops.driverWaits as waits
from selenium.webdriver.support.ui import Select

from nba.classes.NewPlayerId import NewPlayerId
import nba.ops.apiCalls as api
from nba.ops.config import APP_CONFIG

config = APP_CONFIG

def getSalaryDataForDate(date, fantasySite, playerList, driver):
    """
    date in YYYY-MM-DD format
    session is a requests session
    """
    print("Getting salary data for", date)
    baseUrl = config["FC_BASE_URL"]
    projSourceId = 5
    fullUrl = baseUrl + fantasySite + '/NBA/' + date
    page = driver.get(fullUrl)

    # close login popup
    closeLogin = waits.byClass('close-login-alert', driver)
    closeLogin.click()

    # make sure "ALL PLAYERS" is selected
    selectElem = Select(waits.byName('ff_length', driver))
    selectElem.select_by_visible_text("All players")

    # select all salary table rows
    rawHtml = driver.page_source

    tableRowsSelector = 'table#ff tbody tr'

    tree = html.fromstring(rawHtml)
    rows = tree.cssselect(tableRowsSelector)

    salaryData = {
        'currentPlayerSalaries': [],
        'missingPlayerIds': []
    }

    for row in rows:
        try:
            fcId = row.get('data-playerid')
            playerName = row[0].cssselect('span.player-stats')[0].text_content().strip()
            playerObj = next((player for player in playerList if player["fc_id"] == fcId), None)
            salary = int(row[5].text_content().strip())
            
            if playerObj is None:
                # Add data for new source ids:
                newPlayerId = NewPlayerId(projSourceId, fcId, playerName)
                salaryData['missingPlayerIds'].append(newPlayerId.__dict__)
            else:
                if fantasySite == 'fanduel':
                    site = 'FAN_DUEL'
                elif fantasySite == 'draftkings':
                    site = 'DRAFT_KINGS'

                salaryObj = {
                    'playerId': playerObj["player_id"],
                    'gameDate': date,
                    'salary': salary,
                    'site': site
                }

                salaryData['currentPlayerSalaries'].append(salaryObj)
        except Exception as e:
            continue

    return salaryData
