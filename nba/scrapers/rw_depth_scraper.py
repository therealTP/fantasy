import json
import requests
import csv
import datetime
from lxml import html

with open('./../config.json') as config_file:
    config = json.load(config_file)

def getBrefIdToPlayerIdDict():
    # import player id as dict
    with open('./../local-data/bref-id-to-player-id.json') as data_file:
        playerIdDict = json.load(data_file)

    return playerIdDict

def getRawDepthChartTree(sessionObj):
    # Post login data to login form
    sessionObj.post(config["RW_LOGIN_URL"], data=config["RW_CREDS"])

    # Get RAW HTML from projections page
    get_data = sessionObj.get(config["DEPTH_CHART_URL"])

    # Build HTML tree from raw HTML <text></text>
    tree = html.fromstring(get_data.text)

    return tree

def getPlayerDataFromTree(tree):
    rowDivs = tree.cssselect('.container.whitebg:not(.no-print) > div')
    allPlayerData = {}

    for div in rowDivs:
        divClass = div.get('class')

        if divClass == 'span49 nfldepth-teamhead-compact':
            currentTeam = div.cssselect('a')[0].get('href').split("=")[1]

        elif divClass in ['offset1 span9 nfldepth-posblock', 'span9 nfldepth-posblock']:
            usualPosDepth = 1 # keep count of usual pos depth 
            currPosDepth = 1 # keep count of actual pos depth
            playerRows = div.cssselect('div > div.span9')

            for player in playerRows:
                playerId = player.cssselect('a')[0].get('href').split("=")[1]
                playerName = player.cssselect('a')[0].text_content()

                allPlayerData[playerId] = {
                    "team": currentTeam,
                    "playerName": playerName,
                }

                # get player's highest "usual" position on depth chart
                # i.e. where would that player be if not injured/inactive?
                try:
                    if allPlayerData[playerId]["depthPos"] < usualPosDepth:
                        allPlayerData[playerId]["depthPos"] = usualPosDepth
                except KeyError:
                    allPlayerData[playerId]["depthPos"] = usualPosDepth

                usualPosDepth += 1

                notPlayingTags = player.cssselect('a + span')

                if len(notPlayingTags) > 0:
                    # notPlayingLabels = ["OUT", "OUT (S)", "GTD", "INACTIVE"]
                    notPlayingTag = notPlayingTags[0].text_content()
                    allPlayerData[playerId]["currentDepth"] = None
                    allPlayerData[playerId]["status"] = notPlayingTag
                    allPlayerData[playerId]["notPlaying"] = True
                    allPlayerData[playerId]["isStarting"] = False

                elif len(notPlayingTags) == 0:
                    try:
                        # if current player depth exists & is less than new:
                        if allPlayerData[playerId]["currentDepth"] < currPosDepth:
                            allPlayerData[playerId]["currentDepth"] = currPosDepth
                    except KeyError: # if doesn't exist, add
                        allPlayerData[playerId]["currentDepth"] = currPosDepth
                        allPlayerData[playerId]["status"] = 'ACTIVE'
                        allPlayerData[playerId]["notPlaying"] = False

                    if allPlayerData[playerId]["currentDepth"] == 1:
                        allPlayerData[playerId]["isStarting"] = True
                    else:
                        allPlayerData[playerId]["isStarting"] = False

                    # increment after successful add of active player w/ depth pos
                    currPosDepth += 1

    print(allPlayerData)

# start session
session = requests.Session()

htmlTree = getRawDepthChartTree(session)
getPlayerDataFromTree(htmlTree)