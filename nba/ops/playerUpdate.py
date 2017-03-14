import json
import nba.scrapers.rw_depth_scraper as rw
import nba.scrapers.player_info_scraper as pl
import nba.ops.apiCalls as api
import nba.ops.jsonData as jsonData

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
            sourceIds = {}
            options = ["nf_id", "rw_id", "bm_id", "fp_id"]

            for id in options:
                # if new source id exists for player:
                if idsByPlayer[id] is not None:
                    # attach it
                    sourceIds[id] = idsByPlayer[id]
                # if source id already exists for player:
                elif currentPlayerMatch[id] is not None:
                    # attach it:
                    sourceIds[id] = currentPlayerMatch[id]
                # else if no current id or new id exists:
                else:
                    sourceIds[id] = None
                                                            
        # add ids to player dict
        sourceIdUpdates[currentPlayerMatch["player_id"]] = sourceIds

    return sourceIdUpdates

def updateSourceIdsForPlayersManual():
    '''
    Requires manual input from user to match player name/ brefId
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
            # TODO: figure out what to do when no player matches exact name. 
            # check similar name matches

            # if match, add to sourceIdUpdates

            # if none, 
            
            playerBrefId = input("What is the BREF_ID for " + idsByPlayer["player_name"] + "? ")
        # if there is a match:
        else:
            # add ids to player dict
            sourceIdUpdates[currentPlayerMatch["player_id"]] = idsByPlayer

            # NOTE: will override all existing source ids for these players

    return sourceIdUpdates

# print(updateSourceIdsForPlayersAuto())
