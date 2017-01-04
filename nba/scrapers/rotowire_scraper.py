from lxml import html
import json

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

    return driver.page_source

def extractProjections(rawHtml, currentPlayers, games):
    """
    Create tree of HTML from page
    Extract relevant data from tree
    Compile/ return projection dict
    """
    tree = html.fromstring(rawHtml)
    projSourceId = 3

    projectionData = {
        'projections': [],
        'newPlayerIds': []
    }

    # create array of all rows in table body
    for data in tree.cssselect('tbody tr.dproj-precise'):
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

            game = next(game for game in games if game["away_team_id"] == playerObj["current_team"] or game["home_team_id"] == playerObj["current_team"])
            gameId = game["game_id"]

            projection = NbaProjection(playerObj["player_id"], gameId, projSourceId, mins, pts, reb, ast, stl, blk, tov, tpt)
            projectionData['projections'].append(projection.__dict__)

    return projectionData
