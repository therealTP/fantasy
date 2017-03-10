import requests
import json
import time
import nba.ops.logger as logger

# import config file
with open('./../config.json') as config_file:
    config = json.load(config_file)

apiHeaders = {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + config["API_TOKEN"]
}

baseApiUrl = config["API_URL"] + ":" + str(config["API_PORT"])

def ifApiErrorLog(call, responseObj):
    if responseObj.status_code != 200:
        print("ERROR WITH", call)
        logger.logApiError(call)

# GET current player data from db
def getCurrentPlayerData():
    getPlayersUrl = baseApiUrl + "/players"
    getPlayers = requests.get(getPlayersUrl, headers=apiHeaders)
    ifApiErrorLog('GET_PLAYERS', getPlayers)
    playerData = getPlayers.json()
    return playerData

def getIncompletePlayers():
    getIncPlayersUrl = baseApiUrl + "/players?status=INCOMPLETE"
    incPlayers = requests.get(getIncPlayersUrl, headers=apiHeaders).json()
    return incPlayers

# add new players to db:
def postNewPlayers(newPlayerData):
    if len(newPlayerData) > 0:
        postPlayerUrl = baseApiUrl + '/players'
        try:
            post = requests.post(postPlayerUrl, headers=apiHeaders, data=json.dumps(newPlayerData))
        except:
            print("COULDN'T POST PLAYER DATA")

def postNewIncompletePlayers(incPlayerData):
    if len(incPlayerData) > 0:
        postIncPlayerUrl = baseApiUrl + '/players/incomplete'
        try:
            post = requests.post(postIncPlayerUrl, headers=apiHeaders, data=json.dumps(incPlayerData))
        except:
            print("COULDN'T POST INCOMPLETE PLAYER DATA")

# update players already in db
def updateCurrentPlayers(updates):
    # update players that already have rw ids in db
    for currentPlayer in updates:
        updatePlayerUrl = baseApiUrl + '/players/' + str(currentPlayer["playerId"])
        try:
            update = requests.put(updatePlayerUrl, headers=apiHeaders, data=json.dumps(currentPlayer))
        except:
            print("COULDN'T UPDATE ", str(currentPlayer["playerId"]))
            continue

# update incomplete players w/ missing bios
def updatePlayerBios(updates):
    for currentPlayer in updates:
        updatePlayerUrl = baseApiUrl + '/players/' + str(currentPlayer["playerId"]) + '/bio'
        try:
            update = requests.put(updatePlayerUrl, headers=apiHeaders, data=json.dumps(currentPlayer))
        except:
            print("COULDN'T UPDATE ", str(currentPlayer["playerId"]))
            continue


def postPlayersNotOnRosters(idArr):
    if len(idArr) > 0:
        try:
            notOnRosterUrl = baseApiUrl + '/players/notOnRoster'
            post = requests.post(notOnRosterUrl, headers=apiHeaders, data=json.dumps(idArr))
        except:
            print("COULDN'T POST PLAYERS NOT ON ROSTERS")

# --- SOURCE IDS --- #
def getNewSourceIds():
    try:
        newSourceIdsUrl = baseApiUrl + '/newIds'
        newSourceIds = requests.get(newSourceIdsUrl, headers=apiHeaders).json()
        return newSourceIds
    except:
        print("COULDN'T POST PLAYERS NOT ON ROSTERS")

def postNewIds(newIdArr):
    postNewIdsUrl = baseApiUrl + "/newIds"
    postResponse = requests.post(postNewIdsUrl, headers=apiHeaders, data=json.dumps(newIdArr))
    return postResponse

# update current players w/ new source ids
def updatePlayerSourceIds(updates):
    for playerId, newSourceIds in updates.items():
        updatePlayerSourceIdUrl = baseApiUrl + '/players/' + str(playerId) + '/sourceIds'
        try:
            response = requests.put(updatePlayerSourceIdUrl, headers=apiHeaders, data=json.dumps(newSourceIds))
            # if successfully updated player, delete those new source ids:
            if response.status_code == 200:
                deletePlayerSourceIdsUrl = baseApiUrl + '/newIds/' + str(playerId)
                delResponse = requests.delete(deletePlayerSourceIdsUrl, headers=apiHeaders)
        except:
            print("COULDN'T UPDATE ", str(playerId))
            continue

# ---- GAMES ---- #
def getTodaysGames():
    today = time.strftime('%Y-%m-%d')
    getGamesUrl = baseApiUrl + "/games?game_date=" + today
    gameData = requests.get(getGamesUrl, headers=apiHeaders).json()
    return gameData

def getGamesForDate(gameDate):
    getGamesUrl = baseApiUrl + "/games?game_date=" + gameDate
    gameData = requests.get(getGamesUrl, headers=apiHeaders).json()
    return gameData

def getGamesInRange(startDate, endDate):
    getGamesUrl = baseApiUrl + "/games?min_date=" + startDate + "&max_date=" + endDate
    gameData = requests.get(getGamesUrl, headers=apiHeaders).json()
    return gameData

# --- PROJECTIONS --- #
def postProjections(projectionArr):
    postProjsUrl = baseApiUrl + "/projections"
    postResponse = requests.post(postProjsUrl, headers=apiHeaders, data=json.dumps(projectionArr))
    return postResponse

# --- ACTUAL STATS --- #
def getActualStats(date=None):
    if date != None:
        getStatsUrl = baseApiUrl + "/stats?game_date=" + date
    else:
        getStatsUrl = baseApiUrl + "/stats"

    statsData = requests.get(getStatsUrl, headers=apiHeaders).json()
    return statsData

def postActualStats(statsArr):
    postStatsUrl = baseApiUrl + "/stats"
    postResponse = requests.post(postStatsUrl, headers=apiHeaders, data=json.dumps(statsArr))

# --- ML DATA --- #
def getBaseMlData(gameDate, statType, isTraining, numGames):
    if isTraining is True:
        isTrainingStr = "true"
    else:
        isTrainingStr = "false"

    getMlDataUrl = (baseApiUrl + "/mldata?game_date=" + str(gameDate) + 
                    "&stat_type=" + statType + 
                    "&is_training=" + isTrainingStr +
                    "&num_recent_games=" + str(numGames))

    try:
        mlData = requests.get(getMlDataUrl, headers=apiHeaders).json()
        return mlData
    except Exception as e:
        print("COULDN'T GET ML DATA", e)

# --- PREDICTION DATA --- #
def getPredictions(predSrc, gameDate):
    '''
    predSrc = GOOGLE or AZURE
    '''
    getPredictionsUrl = baseApiUrl + '/predictions?date=' + gameDate + '&source=' + predSrc
    predictions = requests.get(getPredictionsUrl, headers=apiHeaders).json()
    return predictions

def postPredictions(predSrc, gameDate, statType, predictionArr):
    '''
    predSrc = GOOGLE or AZURE
    '''
    postPredictionsUrl = baseApiUrl + '/predictions'

    body = {
        'source': predSrc,
        'gameDate': gameDate,
        'statType': statType,
        'predictions': predictionArr
    }

    postResponse = requests.post(postPredictionsUrl, headers=apiHeaders, data=json.dumps(body))

    return postResponse

def postSalaries(salaries):
    '''
    predSrc = GOOGLE or AZURE
    '''
    postPredictionsUrl = baseApiUrl + '/salaries'

    body = salaries

    postResponse = requests.post(postPredictionsUrl, headers=apiHeaders, data=json.dumps(body))

    return postResponse.json()

# -- ANALYTICS --- #
# def getPredictionsVsActual():




