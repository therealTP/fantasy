import json
import requests
import nba.scrapers.rw_depth_scraper as rw
import nba.scrapers.player_info_scraper as pl
import nba.ops.apiCalls as api
import nba.ops.jsonData as jsonData
import nba.ops.logger as logger
from difflib import get_close_matches

from nba.ops.config import APP_CONFIG

config = APP_CONFIG

# function to check if relevant player data has changed
def hasPlayerDataChanged(playerDbData, playerUpdateData):
    needsUpdate = (playerDbData["current_depth_pos"] != playerUpdateData["currentDepth"] or
                    playerDbData["usual_depth_pos"] != playerUpdateData["depthPos"] or
                    playerDbData["status"] != playerUpdateData["status"] or
                    playerDbData["current_team"] != playerUpdateData["team"] or
                    playerDbData["is_starter"] != playerUpdateData["isStarting"] or
                    playerDbData["inactive"] != playerUpdateData["inactive"])

    return needsUpdate

def getDepthChartData(sessionObj):
    '''
    Calls rw depth scraper fcns
    Parses data into dict based on new/current players 
    Returns dict
    '''
    # import team ids as dict
    teamDict = jsonData.TEAM_ABBREV_TO_ID

    # get 
    currPlayerData = api.getCurrentPlayerData()

    # scrape current depth chart data & starting lineup data from rw
    htmlTree = rw.getRawDepthChartTree(sessionObj, config)
    currentDepths = rw.getPlayerDataFromTree(htmlTree, teamDict)

    playerIdsOnRosters = []
    
    playerDataUpdates = {
        "rwIdInDbUpdates": [],
        "rwIdNotInDbPosts": []
    }

    # for each player in current depths, check if they are in DB:
    for rwId, rwData in currentDepths.items():
        try:
            matchedPlayer = next((player for player in currPlayerData if player["rw_id"] == rwId), None)
            rwData["playerId"] = matchedPlayer["player_id"]

            # if player is already incomplete in DB, don't override w new status
            if matchedPlayer["status"] == 'INCOMPLETE':
                rwData["status"] = 'INCOMPLETE'

            # add player id to arr for later check
            playerIdsOnRosters.append(matchedPlayer["player_id"])

            # only update data if player data has changed to save api calls/ db writes
            if hasPlayerDataChanged(matchedPlayer, rwData):
                playerDataUpdates["rwIdInDbUpdates"].append(rwData)
        except: # if no match for rw_id, add player to rwNotInDbArr
            rwData["rw_id"] = rwId
            playerDataUpdates["rwIdNotInDbPosts"].append(rwData)
    
    # create arr of playerIds not on a roster 
    playerDataUpdates["playersNotOnRoster"] = [player["player_id"] for player in currPlayerData if player["player_id"] not in playerIdsOnRosters and player["status"] != 'NOT_ON_ROSTER']

    return playerDataUpdates

def getNewPlayerData(sessionObj, newPlayerArr):
    newPlayers = {
        'complete': [],
        'incomplete': []
    }
    # for all players w/o a rw_id:
    for newPlayer in newPlayerArr:
        # go to rw page
        playerName = pl.getRwInfoForPlayer(newPlayer["rw_id"], sessionObj)
        newPlayer["playerName"] = playerName

        # try to get brefId for name:
        brefId = pl.getBrefIdFromName(playerName, sessionObj)
        # print(brefId)

        # if brefId found for name:
        if brefId != None:
            # get all bref info for player:
            newPlayer["bref_id"] = brefId
            playerInfo = pl.getPlayerInfo(brefId, sessionObj)
            for key, val in playerInfo.items():
                newPlayer[key] = val
            newPlayers["complete"].append(newPlayer)
        
        # or, if brefId not found for player
        elif brefId is None:
            newPlayer["status"] = 'INCOMPLETE'
            newPlayers["incomplete"].append(newPlayer)
    
    return newPlayers

def getBiosForIncompletePlayers(sessionObj, incPlayersArr):
    playerBios = []

    for player in incPlayersArr:
        playerBio = {"playerId": player["player_id"]}
        playerBrefId = input("What is the BREF_ID for " + player["player_name"] + "? ")
        try:
            playerInfo = pl.getPlayerInfo(playerBrefId, sessionObj)
            for key, val in playerInfo.items():
                playerBio[key] = val
            playerBios.append(playerBio)
        except:
            print("Can't pull player info for player with bref_id of ", playerBrefId)
            continue
    
    return playerBios

def mapNewSourceIdsToExistingPlayer(newIdsByPlayer, currentPlayerObj):
    sourceIds = {}
    options = ["nf_id", "rw_id", "bm_id", "fp_id", "fc_id"]

    for id in options:
        # if new source id exists for player:
        if newIdsByPlayer[id] is not None:
            # attach it
            sourceIds[id] = newIdsByPlayer[id]
        # if source id already exists for player:
        elif currentPlayerObj[id] is not None:
            # attach it:
            sourceIds[id] = currentPlayerObj[id]
        # else if no current id or new id exists:
        else:
            sourceIds[id] = None

    return sourceIds

# def getFinalNewPlayerObject(playerName, idsByPlayer, sessionObj):
#     altBrefId = input("What is the BREF_ID for " + playerName + "? ")
#     newPlayerInfo = pl.getPlayerInfo(altBrefId, sessionObj)
#     finalNewPlayerObj = {**newPlayerInfo, **idsByPlayer}
#     finalNewPlayerObj["bref_id"] = altBrefId
#     finalNewPlayerObj["rw_id"] = input("What is the RW_ID for " + playerName + "? ")
#                   status = 'NOT_ON_ROSTER',
#               current_depth_pos = NULL,
#               usual_depth_pos = NULL,
#               current_team = NULL,
#               is_starter = false,
#               inactive = true

def getSourceIdUpdatesForPlayersAuto():
    '''
    Will auto update all players w/ source ids that have an exact name match
    NOTE: will override all existing source ids for any player that matches
    '''
    # get new source ids
    newSourceIdsByPlayer = api.getNewSourceIds()

    # get list of current players
    currentPlayers = api.getCurrentPlayerData()

    # arr to hold update
    sourceIdUpdates = {}

    for idsByPlayer in newSourceIdsByPlayer:
        currentPlayerMatch = next((player for player in currentPlayers if player["player_name"] == idsByPlayer["player_name"]), None)

        # if name does not EXACTLY match any existing player:
        if currentPlayerMatch is None:
            continue
        # if there is a match:
        else:
            sourceIds = mapNewSourceIdsToExistingPlayer(idsByPlayer, currentPlayerMatch)
                                                            
        # add ids to player dict
        sourceIdUpdates[currentPlayerMatch["player_id"]] = sourceIds

    return sourceIdUpdates

def updateSourceIdsForPlayersManualAndLog():
    '''
    Requires manual input from user to match player name/ brefId
    '''
    # get new source ids
    newSourceIdsByPlayer = api.getNewSourceIds()

    # get list of current players
    currentPlayers = api.getCurrentPlayerData()
    allPlayerNames = list((player["player_name"] for player in currentPlayers))

    # arr to hold updates
    existingPlayerSourceIdUpdates = {}

    for idsByPlayer in newSourceIdsByPlayer:
        playerName = idsByPlayer["player_name"]
        # check to see if player matches exact name
        currentPlayerMatch = next((player for player in currentPlayers if player["player_name"] == playerName), None)

        # if name does not EXACTLY match any existing player:
        if currentPlayerMatch is None:
            # check similar name matches
            closestNameMatches = get_close_matches(playerName, allPlayerNames)

            # if match, prompt user to determine which one:
            if len(closestNameMatches) > 0:
                indexMatch = int(input("Does " + playerName + " match any of these players? (Enter the number, or '0' for none.) " + str(closestNameMatches) + " "))
                
                # if no match by name of exisiting, continue/skip, don't need to add:
                if indexMatch == 0:
                    continue
                    # finalNewPlayerObj = getFinalNewPlayerObject(playerName, idsByPlayer, sessionObj)
                    # newPlayers.append(finalNewPlayerObj)
                # if match, assign to current player & add to arr
                elif indexMatch > 0 and indexMatch <= len(closestNameMatches):
                    playerNameMatch = closestNameMatches[indexMatch - 1]
                    currentPlayerMatch = next((player for player in currentPlayers if player["player_name"] == playerNameMatch), None)
                    newSourceIds = mapNewSourceIdsToExistingPlayer(idsByPlayer, currentPlayerMatch)
                    existingPlayerSourceIdUpdates[currentPlayerMatch["player_id"]] = newSourceIds

            # if no name matches, skip, no need to add (will be added if in lineup from RW)
            elif len(closestNameMatches) == 0:
                continue
                # finalNewPlayerObj = getFinalNewPlayerObject(playerName, idsByPlayer, sessionObj)
                # newPlayers.append(finalNewPlayerObj)
        
        # if there is an exact match:
        else:
            # skip over auto match ones, save for later
            continue

    # make source id updates (will also delete the ones that were just updated)
    api.updatePlayerSourceIds(existingPlayerSourceIdUpdates)

    logger.logSourceIdsUpdate(existingPlayerSourceIdUpdates, 'MANUAL')

    return existingPlayerSourceIdUpdates

def updatePlayerSourceIdsAutoAndLog():
    # get all new source ids
    sourceIdUpdates = getSourceIdUpdatesForPlayersAuto()

    # make source id updates (will also delete the ones that were just updated)
    api.updatePlayerSourceIds(sourceIdUpdates)

    # TODO: write this log method
    logger.logSourceIdsUpdate(sourceIdUpdates, 'AUTO')

    return sourceIdUpdates

def updateAllPlayerDataAndLog():
    # create new requests session
    session = requests.Session()

    # get current depth chart data (updates for current players & new players)
    depthChartData = getDepthChartData(session)

    # update current players
    api.updateCurrentPlayers(depthChartData["rwIdInDbUpdates"])

    # get player info for all new players from depth chart data
    newPlayerData = getNewPlayerData(session, depthChartData["rwIdNotInDbPosts"])

    # post new players to api
    api.postNewPlayers(newPlayerData["complete"])
    api.postNewIncompletePlayers(newPlayerData["incomplete"])

    # deactivate all players not on rosters (that aren't already deactivated')
    api.postPlayersNotOnRosters(depthChartData["playersNotOnRoster"])

    # log success
    logger.logPlayerUpdateSuccess(depthChartData["rwIdInDbUpdates"], newPlayerData, depthChartData["playersNotOnRoster"])

def manualUpdateIncompletePlayersAndLog():
    # create new requests session
    session = requests.Session()

    # 1. Update incomplete players
    # get all incomplete players
    incompletePlayers = api.getIncompletePlayers()

    # get bio data for all incomplete players (manually enter brefIds)
    playerBios = getBiosForIncompletePlayers(session, incompletePlayers)

    # make api call to update those players
    api.updatePlayerBios(playerBios)

    #log update
    if len(playerBios) > 0:
        logger.logIncompletePlayersUpdate(playerBios)

# print(updateSourceIdsForPlayersAuto())
