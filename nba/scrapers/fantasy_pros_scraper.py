import json
from lxml import html as html
# import lxml 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import nba.ops.driverWaits as waits 

from nba.classes.NbaProjection import NbaProjection
from nba.classes.NewPlayerId import NewPlayerId
from nba.ops.config import APP_CONFIG

config = APP_CONFIG

def getRawHtml(driver):
    """
    Takes in active selenium driver
    Logs in to FP
    Returns raw html w/ data to scrape
    """
    # go to login page
    driver.get(config["FP_LOGIN_URL"])

    # log in, wait until elem ready
    username = waits.byId(driver, "id_username")
    password = waits.byId(driver, "id_password")

    username.send_keys(config["FP_USERNAME"])
    password.send_keys(config["FP_PW"])

    form = waits.byClass(driver, 'form-horizontal')
    form.submit()

    # go to scrape page
    driver.get(config["FP_SCRAPE_URL"])

    # wait for first projection to load
    # waits.byCss(driver, '.projection-table__body tr:first-child')

    # return scrape page html
    return driver.page_source

def getRawHtmlRequests(sessionObj):
    """
    """
    # get csrf token val & attach to form
    login = sessionObj.get(config["FP_LOGIN_URL"])
    
    login_html = html.fromstring(login.text)
    csrf_input = login_html.xpath(r'//form//input[@type="hidden"]')[0]

    form = config["FP_CREDS"]
    form[csrf_input.attrib["name"]] = csrf_input.attrib["value"]

    headers= {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36",
        "referer": config["FP_LOGIN_URL"]
    }

    result = sessionObj.post(
	    config["FP_LOGIN_URL"], 
	    data = form, 
	    headers = headers
    )

    scrapePage = sessionObj.get(
        config["FP_SCRAPE_URL"], 
        headers = headers
    )

    return scrapePage.content

def extractProjections(rawHtml, currentPlayers, games):
    """
    Create tree of HTML from page
    Extract relevant data from tree
    Compile/ return projection dict
    """
    tree = html.fromstring(rawHtml)
    projSourceId = 4

    rows = tree.cssselect('table#data tbody tr')

    projectionData = {
        'projections': [],
        'newPlayerIds': [],
        'totalNumRows': len(rows)
    }

    # create array of all rows in table body
    for data in rows:
        # extract fpId
        name_link = data.cssselect('td.player-label a.player-name')[0]
        fpId = str(name_link.get('href')).split("/")[3].replace('.php', '')

        # match player w/ rw id
        playerObj = next((player for player in currentPlayers if player["fp_id"] == fpId), None)

        # if no match for fpId:
        if playerObj is None:
            name = str(name_link.text_content()).strip()
            newPlayerId = NewPlayerId(projSourceId, fpId, name)
            projectionData['newPlayerIds'].append(newPlayerId.__dict__)
        # if player is not on a team, skip/don't post projections
        elif playerObj["current_team"] is None:
            continue
        else:
            # extract values of relevant tds in row
            mins = float(data[11].text_content())
            pts = float(data[2].text_content())
            reb = float(data[3].text_content())
            ast = float(data[4].text_content())
            stl = float(data[6].text_content())
            blk = float(data[5].text_content())
            tpt = float(data[9].text_content())
            tov = float(data[12].text_content())

            game = next((game for game in games if game["away_team_id"] == playerObj["current_team"] or game["home_team_id"] == playerObj["current_team"]), None)

            if game is None:
                continue # this only happens rarely, when there's a mismatched player in source data
            else:
                gameId = game["game_id"]

            projection = NbaProjection(playerObj["player_id"], gameId, projSourceId, mins, pts, reb, ast, stl, blk, tov, tpt)
            projectionData['projections'].append(projection.__dict__)

    return projectionData
