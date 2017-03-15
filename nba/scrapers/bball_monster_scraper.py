from lxml import html
import time
from datetime import datetime
from pytz import timezone
import pytz
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json

from nba.classes.NbaProjection import NbaProjection
from nba.classes.NewPlayerId import NewPlayerId
from nba.ops.config import APP_CONFIG

config = APP_CONFIG

def checkForElement(browsObj, elemName):
    '''
    '''
    elem = WebDriverWait(browsObj, 10).until(
        EC.presence_of_element_located((By.NAME, elemName)))

    return elem

def getRawHtml(driver):
    '''
    '''
    driver.get(config["BM_LOGIN_URL"])

    # get user/pass elements
    username = driver.find_element_by_name('ctl00$ContentPlaceHolder1$UsernameTextBox')
    password = driver.find_element_by_name('ctl00$ContentPlaceHolder1$PasswordTextBox')

    # fill in user/pass fields
    username.send_keys(config["BM_USERNAME"])
    password.send_keys(config["BM_PW"])

    # click login button
    login_button = driver.find_element_by_id('ContentPlaceHolder1_LoginButton')
    login_button.click()

    # go to scrape url
    driver.get(config["BM_SCRAPE_URL"])

    update_date = checkForElement(driver, 'UPDATEDATE')

    date_input = checkForElement(driver, 'ctl00$ContentPlaceHolder1$StartDateTextBox')
    date_input.clear()
    # NOTE: date needs to always be in PST
    DATE_FORMAT = '%m/%d/%Y'
    utc_date = datetime.now(tz=pytz.utc)
    todays_date = utc_date.astimezone(timezone('US/Pacific')).strftime(DATE_FORMAT)
    date_input.send_keys(todays_date)
    update_date.click()

    # find select all game box (when loaded) and click
    select_all = checkForElement(driver, 'SELECTALL')
    select_all.click()

    # wait until first checkbox is selected, i.e. all games selected
    WebDriverWait(driver, 10).until(
        EC.element_located_to_be_selected(
            (By.CSS_SELECTOR, "table.dailygamesT tbody tr:first-child td:nth-child(2) input")
        )
    )

    # find refresh data button (when loaded) and click
    refresh_button = checkForElement(driver, 'REFRESH')
    refresh_button.click()

    return driver.page_source

def extractProjections(rawHtml, currentPlayers, games):
    '''
    Create html tree from raw html
    Find & loop through rows of projections, matching w/ currentPlayers
    Return dict containing projections & missing player data
    '''
    tree = html.fromstring(rawHtml)
    projSourceId = 2

    rows = tree.cssselect('table.gridThighlight tbody tr')

    projectionData = {
        'projections': [],
        'newPlayerIds': [],
        'totalNumRows': len(rows)
    }

    # for each row of player data in data table
    for data in rows:
        # if row is a header row, skip it
        if data[2].text_content() == "Rank":
            continue

        # get data from each row's td's
        name_link = data.cssselect('td.tdl a')[0]
        bmId = str(name_link.get('href')).split('=')[1]
        name = name_link.text_content().strip()
        # match player w/ bm id
        playerObj = next((player for player in currentPlayers if player["bm_id"] == bmId), None)

        # if player not in DB:
        if playerObj is None: 
            newPlayerId = NewPlayerId(projSourceId, bmId, name)
            projectionData['newPlayerIds'].append(newPlayerId.__dict__)
        # if player is not on a team, skip/don't post projections
        elif playerObj["current_team"] is None:
            continue
        else:
            mins = float(data[11].text_content())
            pts = float(data[13].text_content())
            reb = float(data[15].text_content())
            ast = float(data[16].text_content())
            stl = float(data[17].text_content())
            blk = float(data[18].text_content())
            tpt = float(data[14].text_content())
            tov = float(data[21].text_content())

            game = next((game for game in games if game["away_team_id"] == playerObj["current_team"] or game["home_team_id"] == playerObj["current_team"]), None)
            
            if game is None:
                continue # this only happens rarely, when there's a mismatched player in source data
            else:
                gameId = game["game_id"]

            projection = NbaProjection(playerObj["player_id"], gameId, projSourceId, mins, pts, reb, ast, stl, blk, tov, tpt)
            projectionData['projections'].append(projection.__dict__)

    return projectionData

