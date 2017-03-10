from lxml import html
import json
import time
import requests

import nba.ops.driverWaits as waits

from nba.classes.NbaProjection import NbaProjection
from nba.classes.NewPlayerId import NewPlayerId

# import config file
with open('./../config.json') as config_file:
    config = json.load(config_file)

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

    '''
    username = waits.byName('username', driver)
    password = waits.byName('p1', driver)

    # fill in user/pass fields
    username.send_keys(config["RW_USERNAME"])
    password.send_keys(config["RW_PW"])

    # click login button
    login_button = waits.byName('submit', driver)
    login_button.click()

    driver.get(config["RW_SCRAPE_URL"])
    # driver.implicitly_wait(3)
    # waits.byCss('.tablesorter tbody tr.dproj-precise:last-child', driver)
    time.sleep(10)
    '''

    return driver.page_source

def getRawHtmlRequests(sessionObj):
    """
    """
    result = sessionObj.post(
	    config["RW_LOGIN_URL"], 
	    data = config["RW_CREDS"], 
	    headers = dict(referer = config["RW_LOGIN_URL"])
    )

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
