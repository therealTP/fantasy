import requests
import json
import csv
from lxml import html
from dateutil import parser

import nba.ops.jsonData as jsonData

# def getBrefIdToPlayerIdDict():
#     # import player id as dict
#     with open('./../local-data/bref-id-to-player-id.json') as data_file:
#         playerIdDict = json.load(data_file)

#     return playerIdDict

# def getBrefIdToPlayerPosDict():
#     # import player id as dict
#     with open('./../local-data/bref-id-to-player-pos.json') as data_file:
#         playerPosDict = json.load(data_file)
    
#     return playerPosDict

def getPostGameDepthCharts(gameSlug, sessionObj, playerList):
    # constants
    BASE_URL = 'http://www.basketball-reference.com/boxscores/'
    URL_EXT = '.html'
    TABLE_ID = '.sortable'

    boxScoreUrl = BASE_URL + gameSlug + URL_EXT
    page = sessionObj.get(boxScoreUrl)
    tree = html.fromstring(page.text)
    selector = 'table' + TABLE_ID
    tables = tree.cssselect(selector)

    gameData = {
        "awayTeam": {
            "players": {
                # id: {depth_pos: 1, starter: true}
            }
        },
        "homeTeam": {
            "players": {
                # id: {depth_pos: 1, starter: true}
            }
        }
    }
    
    awayDepths = {"PG": 1, "SG": 1, "SF": 1, "PF": 1, "C": 1}
    homeDepths = {"PG": 1, "SG": 1, "SF": 1, "PF": 1, "C": 1}

    awayStarterCount = 0
    homeStarterCount = 0

    awayTeamRows = tables[0].cssselect('tbody tr:not(.thead)')
    homeTeamRows = tables[2].cssselect('tbody tr:not(.thead)')
    
    # get away players/ depths/ starters
    for player in awayTeamRows: 
        playerBrefId = player[0].get('data-append-csv')
        # playerObj = next((player for player in playerList if player["bref_id"] == playerBrefId), None)
        # if playerObj != None:
        try:
            # playerPos = posDict[playerBrefId]
            # playerId = idDict[playerBrefId]

            playerObj = next((player for player in playerList if player["bref_id"] == playerBrefId), None)
            if playerObj != None:
                playerId = playerObj["player_id"]
                playerPos = playerObj["player_position"]
                # if player suspended, add to injured arr:
                if player[1].text_content() == 'Player Suspended':
                    gameData["awayTeam"]["injuredPlayers"].append(playerId)
                    continue

                if awayStarterCount < 5:
                    isStarter = True
                    awayStarterCount += 1
                else:
                    isStarter = False

                gameData["awayTeam"]["players"][playerId] = {
                    "depthPos": awayDepths[playerPos],
                    "isStarter": isStarter
                }

                awayDepths[playerPos] += 1
        except KeyError:
            print("MISSING:", playerBrefId)

    # get home players/ depths/ starters
    for player in homeTeamRows: 
        playerBrefId = player[0].get('data-append-csv')

        try:
            # playerPos = posDict[playerBrefId]
            # playerId = idDict[playerBrefId]

            playerObj = next((player for player in playerList if player["bref_id"] == playerBrefId), None)
            if playerObj != None:
                playerId = playerObj["player_id"]
                playerPos = playerObj["player_position"]

                # if player suspended, add to injured arr:
                if player[1].text_content() == 'Player Suspended':
                    gameData["homeTeam"]["injuredPlayers"].append(playerId)
                    continue

                if homeStarterCount < 5:
                    isStarter = True
                    homeStarterCount += 1
                else:
                    isStarter = False

                gameData["homeTeam"]["players"][playerId] = {
                    "depthPos": homeDepths[playerPos],
                    "isStarter": isStarter
                }

                homeDepths[playerPos] += 1
        except KeyError:
            print("MISSING", playerBrefId)

def getBoxScoreData(gameSlug, sessionObj, playerList):
    """
    Used to get box score data for past games that INCLUDE:
    - Depth chart data
    - Injuries
    - Scores
    """
    # constants
    BASE_URL = 'http://www.basketball-reference.com/boxscores/'
    URL_EXT = '.html'
    TABLE_ID = '.sortable'

    boxScoreUrl = BASE_URL + gameSlug + URL_EXT
    page = sessionObj.get(boxScoreUrl)
    tree = html.fromstring(page.text)
    selector = 'table' + TABLE_ID
    tables = tree.cssselect(selector)

    gameData = {
        "awayTeamInactive": [], # ALL inactives
        "homeTeamInactive": []
        # "awayTeamDnp": [],
        # "homeTeamDnp": []
        # attendance:
        # homeTeamPts:
        # awayTeamPts: 
        # homeTeamWin:
    }

    injuryDivSelector = "div#content > div:not(.filter)"
    inactiveSpans = tree.cssselect(injuryDivSelector)[10]

    # keep track of # spans to parse inactives
    spanCount = 0

    # get all inactive players
    for inactive in inactiveSpans:
        if inactive.tag == 'a':
            # try to get injured players
            try:
                brefId = inactive.get('href').split('/')[3].replace(".html", "")
                try:
                    playerObj = next((player for player in playerList if player["bref_id"] == brefId), None)
                    if playerObj != None:
                        playerId = playerObj["player_id"]
                        # if away team:
                        if spanCount == 1:
                            gameData["awayTeamInactive"].append(playerId)
                        elif spanCount == 2:
                            gameData["homeTeamInactive"].append(playerId)
                except KeyError:
                    print("MISSING INJURED", brefId)
            except IndexError: # if none:
                break
        elif inactive.tag == 'span':
            spanCount += 1
        elif inactive.tag == 'br':
            break

    # get points scored
    awayPoints = int(tables[0].cssselect('tfoot td')[18].text_content())
    homePoints = int(tables[2].cssselect('tfoot td')[18].text_content())
    gameData["awayPoints"] = awayPoints
    gameData["homePoints"] = homePoints

    # who won?
    if awayPoints < homePoints:
        gameData["homeTeamWon"] = True
    else:
        gameData["homeTeamWon"] = False

    # attendance
    allTextNodes = [x for x in inactiveSpans.itertext()]
    isAttendance = False
    attendance = 0
    for node in allTextNodes:
        if node != 'Attendance:' and isAttendance == False:
            pass
        elif node == 'Attendance:':
            isAttendance = True
        elif isAttendance is True:
            gameData["attendance"] = int(node.replace('\xa0', '').replace(',',''))
            break

    return gameData

def getDataForAllGames(gameDict, sessionObj, idDict, posDict):
    masterDict = {}
    gamesScraped = 0
    maxGames = 10
    for game in gameDict:
        print("getting data for ", gameDict[game])
        # if gamesScraped > maxGames:
        #     break
        
        masterDict[game] = getBoxScoreData(gameDict[game], sessionObj, idDict, posDict)
        gamesScraped += 1

    print("num games scraped", gamesScraped)

    return masterDict

def getDataForSomeGames(gamesArr, gameDict, sessionObj, idDict, posDict):
    gamesData = {}
    for game in gamesArr:
        print("getting data for ", gameDict[game])
        gamesData[game] = getBoxScoreData(gameDict[game], sessionObj, idDict, posDict)
    
    return gamesData



# # import team json as dict
# with open('./../local-data/game-id-to-bref-url.json') as data_file:    
#     gameUrlDict = json.load(data_file)

# # get relevant dicts
# idDict = getBrefIdToPlayerIdDict()
# posDict = getBrefIdToPlayerPosDict()

# # start session
# session = requests.Session()

# gamesToRescrape = ["10209", "11138", "10208", "10213", "11141", "11137", "10211", "10212", "11140", "10210", "11139"]