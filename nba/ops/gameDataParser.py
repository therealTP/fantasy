import json
import csv

def getGameIdLookupDict():
    with open('./../local-data/game-id-lookup.json') as data_file:
        gameIdDict = json.load(data_file)

    return gameIdDict

def getGameLogData():
    with open('./../scraped-data/new-game-logs.json') as data_file:
        gameLogs = json.load(data_file)

    return gameLogs

def getGameDataFromGameLogs(gameLogs, gameIdDict):
    gameData = []
    for gameId, data in gameLogs.items():
        # [game_id, home_team_won, attendance, home_team_pts, away_team_pts, [home_team_injured], [away_team_injured]]
        gameRow = [] 

        try:
            # get data
            homeWon =       data["post"]["homeTeamWon"]
            attend =        data["post"]["attendance"]
            homePts =       data["post"]["homePoints"]
            awayPts =       data["post"]["awayPoints"]
            homeInj =       "{" + str(data["homeTeam"]["injuredPlayers"]).strip("[]") + "}"       
            awayInj =       "{" + str(data["awayTeam"]["injuredPlayers"]).strip("[]") + "}"   
            # add data to row
            gameRow.extend((int(gameId), homeWon, attend, homePts, awayPts, homeInj, awayInj))

            # add row to master arr
            gameData.append(gameRow)

        except KeyError:
            print("PARSE ERROR WITH GAME", gameId)
            continue

    return gameData

def getProjectionDataFromGameLogs(gameLogs, gameIdDict):
    projectionData = []

    # for each game:
    for gameId, gameData in gameLogs.items():
        # loop through home team players:
        for playerId, playerData in gameData["homeTeam"]["players"].items():
            # [player_id, game_date, game_id, team_id, depth_pos, is_starter]
            homeProjectionRow = []
            try:
                # get data
                gameDate =      gameIdDict[gameId]["game_date"]
                teamId =        gameIdDict[gameId]["home_team_id"] # looping through home players
                depthPos =      playerData["depthPos"]
                isStarter =     playerData["isStarter"]
  
                # add data to row
                homeProjectionRow.extend((int(playerId), gameDate, int(gameId), teamId, depthPos, isStarter))

                # add row to master arr
                projectionData.append(homeProjectionRow)

            except KeyError:
                print("PARSE ERROR WITH GAME", gameId)
                continue

        # loop through away team players:
        for playerId, playerData in gameData["awayTeam"]["players"].items():
            # [player_id, game_date, game_id, team_id, depth_pos, is_starter]
            awayProjectionRow = []
            try:
                # get data
                gameDate =      gameIdDict[gameId]["game_date"]
                teamId =        gameIdDict[gameId]["away_team_id"] # looping through home players
                depthPos =      playerData["depthPos"]
                isStarter =     playerData["isStarter"]
  
                # add data to row
                awayProjectionRow.extend((int(playerId), gameDate, int(gameId), teamId, depthPos, isStarter))

                # add row to master arr
                projectionData.append(awayProjectionRow)

            except KeyError:
                print("PARSE ERROR WITH GAME", gameId)
                continue
         
    print("UPDATES FOR ", len(projectionData))
    return projectionData

# gameLogDict = getGameLogData()
# gameIdDict = getGameIdLookupDict()

# projectionUpdateData = getProjectionDataFromGameLogs(gameLogDict, gameIdDict)

with open("./../scraped-data/projection-update-data.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerows(projectionUpdateData)



# print(createGameIdDict())