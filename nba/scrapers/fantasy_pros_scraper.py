import json
from lxml import html

from nba.classes.NbaProjection import NbaProjection
from nba.classes.MissingPlayer import MissingPlayer

# import config file
with open('./../config.json') as config_file:
    config = json.load(config_file)

def getRawHtml(driver):
    """
    Takes in active selenium driver
    Logs in to FP
    Returns raw html w/ data to scrape
    """
    # go to login page
    driver.get(config["FP_LOGIN_URL"])

    # log in
    username = driver.find_element_by_id('id_username')
    password = driver.find_element_by_id('id_password')

    username.send_keys(config["FP_USERNAME"])
    password.send_keys(config["FP_PW"])

    form = driver.find_element_by_class_name('form-horizontal')
    form.submit()

    # go to scrape page
    driver.get(config["FP_SCRAPE_URL"])

    # return scrape page html
    return driver.page_source

def extractProjections(rawHtml, currentPlayers):
    """
    Create tree of HTML from page
    Extract relevant data from tree
    Compile/ return projection dict
    """
    tree = html.fromstring(rawHtml)
    projSourceId = 4

    projectionData = {
        'projections': [],
        'missingPlayers': []
    }

    # create array of all rows in table body
    for data in tree.cssselect('table#data tbody tr'):
        # extract fpId
        name_link = data.cssselect('td.player-label a.player-name')[0]
        fpId = str(name_link.get('href')).split("/")[3].replace('.php', '')

        # match player w/ rw id
        playerObj = next((player for player in currentPlayers if player["fp_id"] == fpId), None)

        # if no match for fpId:
        if playerObj is None:
            name = str(name_link.text_content())
            missingPlayer = MissingPlayer(projSourceId, fpId, name)
            projectionData['missingPlayers'].append(missingPlayer.__dict__)
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

            projection = NbaProjection(playerObj["player_id"], projSourceId, mins, pts, reb, ast, stl, blk, tov, tpt)
            projectionData['projections'].append(projection.__dict__)

    return projectionData
