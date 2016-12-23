import json
import requests
import csv
import datetime
from lxml import html

def getRawDepthChartTree(sessionObj, config):
    # Post login data to login form
    sessionObj.post(config["RW_LOGIN_URL"], data=config["RW_CREDS"])

    # Get RAW HTML from projections page
    get_data = sessionObj.get(config["DEPTH_CHART_URL"])

    # Build HTML tree from raw HTML <text></text>
    tree = html.fromstring(get_data.text)

    return tree

def getPlayerDataFromTree(tree, teamDict):
    rowDivs = tree.cssselect('.container.whitebg:not(.no-print) > div')
    allPlayerData = {}

    for div in rowDivs:
        divClass = div.get('class')
        posDict = {
            "Point Guard": "PG",
            "Shooting Guard": "SG",
            "Small Forward": "SF",
            "Power Forward": "PF",
            "Center": "C"
        }

        # if team header/div, get team data:
        if divClass == 'span49 nfldepth-teamhead-compact':
            currentTeam = div.cssselect('a')[0].get('href').split("=")[1]

        # if pos div w/ player data in it:
        elif divClass in ['offset1 span9 nfldepth-posblock', 'span9 nfldepth-posblock']:
            usualPosDepth = 1 # keep count of usual pos depth 
            currPosDepth = 1 # keep count of actual pos depth
            # currPosition = posDict[div.cssselect('div > div:first-child')[0].text_content()]
            # all players in pos div
            playerRows = div.cssselect('div > div.span9')

            # for each player in pos div
            for player in playerRows:
                playerId = player.cssselect('a')[0].get('href').split("=")[1]
                # playerName = player.cssselect('a')[0].text_content()

                # allPlayerData[playerId] = {
                #     "team": teamDict[currentTeam]
                #     # "playerName": playerName
                # }

                # get player's highest "usual" position on depth chart
                # i.e. where would that player be if not injured/inactive?
                try:
                    if allPlayerData[playerId]["depthPos"] > usualPosDepth:
                        allPlayerData[playerId]["depthPos"] = usualPosDepth
                except KeyError:
                    # In this scenario, player hasn't been added to dict yet:
                    allPlayerData[playerId] = {
                        "depthPos": usualPosDepth,
                        "team": teamDict[currentTeam]
                    }

                usualPosDepth += 1

                notPlayingTags = player.cssselect('a + span')

                if len(notPlayingTags) > 0:
                    # notPlayingLabels = ["OUT", "OUT (S)", "GTD", "INACTIVE"]
                    notPlayingTag = notPlayingTags[0].text_content()
                    allPlayerData[playerId]["currentDepth"] = 0
                    allPlayerData[playerId]["status"] = notPlayingTag
                    allPlayerData[playerId]["inactive"] = True
                    allPlayerData[playerId]["isStarting"] = False
                    # allPlayerData[playerId]["playerPosition"] = currPosition

                elif len(notPlayingTags) == 0:
                    try:
                        # if current player depth exists & is less than new:
                        if allPlayerData[playerId]["currentDepth"] > currPosDepth:
                            allPlayerData[playerId]["currentDepth"] = currPosDepth
                            # allPlayerData[playerId]["playerPosition"] = currPosition
                    except KeyError: # if doesn't exist, add
                        allPlayerData[playerId]["currentDepth"] = currPosDepth
                        # allPlayerData[playerId]["playerPosition"] = currPosition
                        allPlayerData[playerId]["status"] = 'ACTIVE'
                        allPlayerData[playerId]["inactive"] = False

                    if allPlayerData[playerId]["currentDepth"] == 1:
                        allPlayerData[playerId]["isStarting"] = True
                    else:
                        allPlayerData[playerId]["isStarting"] = False

                    # increment after successful add of active player w/ depth pos
                    currPosDepth += 1

    return allPlayerData