from lxml import html
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json

from nba.classes.NbaProjection import NbaProjection

# import config file
with open('./../config.json') as config_file:
    config = json.load(config_file)

def checkForElement(browsObj, elemName):
    """
    """
    elem = WebDriverWait(browsObj, 10).until(
        EC.presence_of_element_located((By.NAME, elemName)))

    return elem

def getRawHtml(driver):
    """
    """
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

    refresh_button = checkForElement(driver, 'UPDATEDATE')

    date_input = checkForElement(driver, 'ctl00$ContentPlaceHolder1$StartDateTextBox')
    date_input.clear()
    todays_date = time.strftime('%m/%d/%Y')
    date_input.send_keys(todays_date)
    refresh_button.click()

    # find select all game box (when loaded) and click
    select_all = checkForElement(driver, 'SELECTALL')
    select_all.click()

    # find refresh data button (when loaded) and click
    refresh_button = checkForElement(driver, 'UPDATEDATE')
    refresh_button.click()

    return driver.page_source


def extractProjections(rawHtml, currentPlayers):
    '''
    Create html tree from raw html
    Find & loop through rows of projections, matching w/ currentPlayers
    Return dict containing projections & missing player data
    '''
    tree = html.fromstring(rawHtml)
    projSourceId = 2

    projectionData = {
        'projections': [],
        'missingPlayers': []
    }

    # for each row of player data in data table
    for data in tree.cssselect('table.gridThighlight tr'):
        # get data from each row's td's
        bmId = str(name_row[0].get('href')).split('=')[1]
        # match player w/ rw id
        playerObj = next((player for player in currentPlayers if player["bm_id"] == bmId), None)

        if playerObj is None:
            
        # if row is a header row, skip it
        if (data[2].text_content()) == "Rank":
            pass
        # if not, extract data from row
        else:
            # select name row
            name_row = data.cssselect('td.tdl a')
            # print (name_row)


            # print (source_id)
            name = name_row[0].text_content()
            pts = float(data[13].text_content())
            reb = float(data[15].text_content())
            ast = float(data[16].text_content())
            stl = float(data[17].text_content())
            blk = float(data[18].text_content())
            tpt = float(data[14].text_content())
            tov = float(data[21].text_content())
            mins = float(data[11].text_content())

            # get universal player id from player_data
            player_id = ps.getPlayerId(source_id, 3, name)

            # if no player_id found, player will be added to queue
            if player_id is None:
                # pass on data entry, do not add proj data for this player
                pass

            entry = ds.createEntry(pts, reb, ast, stl, blk, tov, tpt, mins)

            ds.addEntryToProjectionDict(projection_dict, player_id, entry)

    return projection_dict

