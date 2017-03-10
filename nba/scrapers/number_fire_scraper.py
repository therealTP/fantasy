from lxml import html
import json

import nba.ops.driverWaits as waits

from nba.classes.NbaProjection import NbaProjection
from nba.classes.NewPlayerId import NewPlayerId

"""
NUMBERFIRE
"""

# import config file
with open('./../config.json') as config_file:
    config = json.load(config_file)

def getRawHtml(driver):
    driver.get(config["NF_LOGIN_URL"])

    loginModalLink = waits.byCssClickable("li.login > a", driver)
    loginModalLink.click()

    googleLoginButton = waits.byCssClickable(".modal-container > ul > li > a.button--google", driver)
    googleLoginButton.click()

    googleEmailField = waits.byIdVisible("Email", driver)
    googleEmailField.send_keys(config["NF_USERNAME"])

    nextButton = waits.byIdVisible("next", driver)
    nextButton.click()

    googlePwField = waits.byIdVisible("Passwd", driver)
    googlePwField.send_keys(config["NF_PW"])

    signInButton = waits.byIdVisible("signIn", driver)
    signInButton.click()

    driver.get(config["NF_SCRAPE_URL"])

    # wait for first projection to load
    waits.byCssVisible("tbody.stat-table__body", driver)

    return driver.page_source

def extractProjections(rawHtml, currentPlayers, games):
    """
    Takes in raw html, extracts projections
    Returns arr of projections, ready to post to api
    """
    tree = html.fromstring(rawHtml)
    projSourceId = 1

    # get all rows
    rows = tree.cssselect('tbody.stat-table__body tr')

    projectionData = {
        'projections': [],
        'newPlayerIds': [],
        'totalNumRows': len(rows)
    }

    for row in rows:
        player_link = row[0].cssselect('span.player-info a.full')[0]
        nfSlug = player_link.get('href').split('/')[-1]
        nfId = row.get('data-player-id')
        playerObj = next((player for player in currentPlayers if player["nf_id"] == nfId or player["nf_id"] == nfSlug), None)

        # if no playerId for nfId:
        if playerObj is None:
            name = player_link.text_content().replace('"', '').strip()
            newPlayerId = NewPlayerId(projSourceId, nfId, name)
            projectionData['newPlayerIds'].append(newPlayerId.__dict__)
        # if player is not on a team, skip/don't post projections
        elif playerObj["current_team"] is None:
            continue
        else:
            # get stats
            mins = float(row[4].text_content())
            pts = float(row[5].text_content())
            reb = float(row[6].text_content())
            ast = float(row[7].text_content())
            stl = float(row[8].text_content())
            blk = float(row[9].text_content())
            tov = float(row[10].text_content())
            # NF doesn't do tpt projs
            tpt = None

            game = next((game for game in games if game["away_team_id"] == playerObj["current_team"] or game["home_team_id"] == playerObj["current_team"]), None)

            if game is None:
                # this only happens rarely, when there's a mismatched player in source data
                # or, if pulling from
                continue 
            else:
                gameId = game["game_id"]

            # init projection obj for each
            projection = NbaProjection(playerObj["player_id"], gameId, projSourceId, mins, pts, reb, ast, stl, blk, tov, tpt)
            projectionData['projections'].append(projection.__dict__)

    return projectionData