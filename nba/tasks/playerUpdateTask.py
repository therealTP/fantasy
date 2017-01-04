'''
This task is run continuously, starting an hr before the game.
Will provide main updates of injuries, depth charts, etc.
'''
import requests
import nba.ops.playerUpdate as pl
import nba.ops.apiCalls as api 

# create new requests session
session = requests.Session()

# get current depth chart data (updates for current players & new players)
depthChartData = pl.getDepthChartData(session)

# update current players
api.updateCurrentPlayers(depthChartData["rwIdInDbUpdates"])

# get player info for all new players from depth chart data
newPlayerData = pl.getNewPlayerData(session, depthChartData["rwIdNotInDbPosts"])

# post new players to api
api.postNewPlayers(newPlayerData["complete"])
api.postNewIncompletePlayers(newPlayerData["incomplete"])

# deactivate all players not on rosters (that aren't already deactivated')
api.postPlayersNotOnRosters(depthChartData["playersNotOnRoster"])
