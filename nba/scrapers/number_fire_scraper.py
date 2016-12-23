from lxml import html
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from nba.classes.NbaProjection import NbaProjection
from nba.classes.MissingPlayer import MissingPlayer

"""
NUMBERFIRE
"""

# import config file
with open('./../config.json') as config_file:
    config = json.load(config_file)

def getRawHtml(driver):
    driver.get(config["NF_LOGIN_URL"])

    loginModalLink = driver.find_element_by_css_selector("li.login > a")
    loginModalLink.click()

    googleLoginButton = driver.find_element_by_css_selector(".modal-container > ul > li > a.button--google")
    googleLoginButton.click()

    googleEmailField = driver.find_element_by_id("Email")
    googleEmailField.send_keys(config["NF_USERNAME"])

    nextButton = driver.find_element_by_id("next")
    nextButton.click()

    googlePwField = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "Passwd"))
    )

    googlePwField.send_keys(config["NF_PW"])

    signInButton = driver.find_element_by_id("signIn")
    signInButton.click()

    driver.get(config["NF_SCRAPE_URL"])

    return driver.page_source

def extractProjections(rawHtml, currentPlayers):
    """
    Takes in raw html, extracts projections
    Returns arr of projections, ready to post to api
    """
    tree = html.fromstring(rawHtml)
    projSourceId = 1

    projectionData = {
        'projections': [],
        'missingPlayers': []
    }

    # player links to get player id is in separate table, so get those links
    playerLinks = tree.cssselect('.projection-table--fixed tbody tr td span a.full')

    # loop w/ index for looking up playerId in playerLinks
    for idx, dataRow in enumerate(tree.cssselect('.projection-table.no-fix .projection-table__body tr')):
        player_link = playerLinks[idx]
        nfId = player_link.get('href').split('/')[-1]
        playerObj = next((player for player in currentPlayers if player["nf_id"] == nfId), None)

        # if no playerId for nfId:
        if playerObj is None:
            name = player_link.text_content().strip()
            missingPlayer = MissingPlayer(projSourceId, nfId, name)
            projectionData['missingPlayers'].append(missingPlayer.__dict__)
        else:
            # get stats
            mins = float(dataRow[3].text_content())
            pts = float(dataRow[4].text_content())
            reb = float(dataRow[5].text_content())
            ast = float(dataRow[6].text_content())
            stl = float(dataRow[7].text_content())
            blk = float(dataRow[8].text_content())
            tpt = None
            tov = float(dataRow[9].text_content())

            # init projection obj for each
            projection = NbaProjection(playerObj["player_id"], projSourceId, mins, pts, reb, ast, stl, blk, tov, tpt)
            projectionData['projections'].append(projection.__dict__)

    return projectionData