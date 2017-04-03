from lxml import html
import json
import time
import requests
from datetime import datetime, timedelta, date
import pytz

import nba.ops.driverWaits as waits

from nba.classes.NbaProjection import NbaProjection
from nba.classes.NewPlayerId import NewPlayerId
from nba.classes.NbaGameSpread import NbaGameSpread
import nba.ops.jsonData as jsonData
from nba.ops.config import APP_CONFIG

config = APP_CONFIG

def getRawHtml(driver):
    driver.get(config["RW_LOGIN_URL"])

    username = driver.find_element_by_name('username')
    password = driver.find_element_by_name('p1')

    # fill in user/pass fields
    username.send_keys(config["RW_USERNAME"])
    password.send_keys(config["RW_PW"])

    # click login button
    login_button = driver.find_element_by_name('submit')
    login_button.click()

    driver.get(config["RW_SCRAPE_URL"])
    # time.sleep(10)

    return driver.page_source

def logInRequestsSession(sessionObj):
    """
    Returns a logged in session obj to RW
    """
    result = sessionObj.post(
	    config["RW_LOGIN_URL"], 
	    data = config["RW_CREDS"], 
	    headers = dict(referer = config["RW_LOGIN_URL"])
    )

    return sessionObj

def getRawHtmlRequests(session):
    """
    """
    sessionObj = logInRequestsSession(session)

    scrapePage = sessionObj.get(
        config["RW_SCRAPE_URL"], 
        headers = dict(referer = config["RW_SCRAPE_URL"])
    )

    return scrapePage.content

def extractProjections(rawHtml, currentPlayers, games):
    """
    Create tree of HTML from page
    Extract relevant data from tree
    Compile/ return projection dict
    """
    tree = html.fromstring(rawHtml)
    projSourceId = 3

    rows = tree.cssselect('tbody tr.dproj-precise')

    projectionData = {
        'projections': [],
        'newPlayerIds': [],
        'totalNumRows': len(rows)
    }

    # create array of all rows in table body
    for data in rows:
        # extract player_id
        rwId = str(data.cssselect('a')[0].get('href')).split('=')[1]
        # match player w/ rw id
        playerObj = next((player for player in currentPlayers if player["rw_id"] == rwId), None)

        # if no match for rwId:
        if playerObj is None:
            # get raw name in array from span
            name_arr = str(data.cssselect('span')[0].text_content()).split('\xa0')
            name = str(name_arr[1]) + " " + str(name_arr[0]).strip().replace("  ", " ")
            newPlayerId = NewPlayerId(projSourceId, rwId, name)
            projectionData['newPlayerIds'].append(newPlayerId.__dict__)
        # if player is not on a team, skip/don't post projections
        elif playerObj["current_team"] is None:
            # print("NO PLAYER TEAM!")
            continue
        else:
            
            mins = float(data[4].text_content())
            pts = float(data[5].text_content())
            reb = float(data[6].text_content())
            ast = float(data[7].text_content())
            stl = float(data[8].text_content())
            blk = float(data[9].text_content())
            tpt = float(data[10].text_content())
            tov = float(data[13].text_content())

            game = next((game for game in games if game["away_team_id"] == playerObj["current_team"] or game["home_team_id"] == playerObj["current_team"]), None)

            if game is None:
                continue # this only happens rarely, when there's a mismatched player in source data
            else:
                gameId = game["game_id"]

            projection = NbaProjection(playerObj["player_id"], gameId, projSourceId, mins, pts, reb, ast, stl, blk, tov, tpt)
            projectionData['projections'].append(projection.__dict__)

    return projectionData

# -- SALARY SCRAPERS --- #
def getRawHtmlForSalaries(session):
    sessionObj = logInRequestsSession(session)

    salaryPage = sessionObj.get(
        config["RW_SALARIES_URL"], 
        headers = dict(referer = config["RW_SALARIES_URL"])
    )

    return salaryPage.content

def extractSalaries(rawHtml, currentPlayers):

    tree = html.fromstring(rawHtml)
    rows = tree.cssselect('tbody#players tr')
    projSourceId = 3

    salaryData = {
        'newPlayerIds': [],
        'currentPlayerSalaries': []
    }

    # create array of all rows in table body
    for data in rows:
        # extract player_id
        rwId = data.get('data-playerid')
        # match player w/ rw id
        playerObj = next((player for player in currentPlayers if player["rw_id"] == rwId), None)

        # if no match for rwId:
        if playerObj is None:
            # get raw name in array from span
            name = data.cssselect('a.dplayer-link')[0].text_content().strip().replace("  ", " ").replace("'", "")
            newPlayerId = NewPlayerId(projSourceId, rwId, name)
            salaryData['newPlayerIds'].append(newPlayerId.__dict__)
        # if player is not on a team, skip/don't post projections
        else:
            salary = int(data[5].text_content().replace('$', '').replace(',', ''))

            DATE_FORMAT = '%Y-%m-%d'
            today_pst = datetime.now(tz=pytz.utc).astimezone(pytz.timezone('US/Pacific')).strftime(DATE_FORMAT)

            # TODO: handle multiple sources, DRAFT_KINGS
            salaryObj = {
                'playerId': playerObj["player_id"],
                'gameDate': today_pst,
                'salary': salary,
                'site': 'FAN_DUEL'
            }

            salaryData['currentPlayerSalaries'].append(salaryObj)
            
    return salaryData

def getRawHtmlForSpreads(session):
    sessionObj = logInRequestsSession(session)

    spreadsPage = sessionObj.get(
        config["RW_SPREADS_URL"], 
        headers = dict(referer = config["RW_SPREADS_URL"])
    )

    return spreadsPage.content

def extractSpreads(rawHtml, gamesToMatch):
    """
    arr of games from db to match
    """
    tree = html.fromstring(rawHtml)
    games = tree.cssselect('div#dfsPanelsOn div.compact-filter ~ div.span49')[1:]
    teamDict = jsonData.TEAM_ABBREV_TO_ID

    spreadData = []

    for game in games:
        awayTeamAbbr = game.cssselect('div.advlineup-topboxleft img')[0].get('src').split("/")[-1].split(".")[0].replace("100", "")
        homeTeamAbbr = game.cssselect('div.advlineup-topboxright img')[0].get('src').split("/")[-1].split(".")[0].replace("100", "")
        awayTeamId = teamDict[awayTeamAbbr]
        homeTeamId = teamDict[homeTeamAbbr]

        gameObj = next((game for game in gamesToMatch if game["away_team_id"] == awayTeamId and game["home_team_id"] == homeTeamId), None)

        # if no match, return
        if gameObj is None:
            return "SPREAD GAME DOESNT MATCH"

        awayPredPts = float(game.cssselect('div.advlineup-oddsbar .advlineup-vegasleft > div')[1].text_content().split(" ")[-1])
        homePredPts = float(game.cssselect('div.advlineup-oddsbar .advlineup-vegasright > div')[0].text_content().split(" ")[-1])

        spreadObj = NbaGameSpread(gameObj['game_id'], awayPredPts, homePredPts)

        spreadData.append(spreadObj.__dict__)

    return spreadData
