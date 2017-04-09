import requests
import json
import time
from datetime import datetime
from pytz import timezone
import pytz
import nba.ops.logger as logger
from nba.ops.config import APP_CONFIG

# import config file
config = APP_CONFIG

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

# update incomplete players w/ missing bios
def updatePlayerPositions(updates):
    for positionUpdate in updates:
        updatePlayerUrl = baseApiUrl + '/players/' + str(positionUpdate["playerId"]) + '/position'
        try:
            update = requests.put(updatePlayerUrl, headers=apiHeaders, data=json.dumps(positionUpdate))
        except:
            print("COULDN'T UPDATE ", str(positionUpdate["playerId"]))
            continue


def postPlayersNotOnRosters(idArr):
    if len(idArr) > 0:
        try:
            notOnRosterUrl = baseApiUrl + '/players/notOnRoster'
            post = requests.post(notOnRosterUrl, headers=apiHeaders, data=json.dumps(idArr))
        except:
            print("COULDN'T POST PLAYERS NOT ON ROSTERS")

# get counts of pending manual updates 
def getPendingManualUpdatesCounts():
    getPendingUpdatesUrl = baseApiUrl + "/players/pending"
    pendingUpdates = requests.get(getPendingUpdatesUrl, headers=apiHeaders).json()[0]
    return pendingUpdates

# --- SOURCE IDS --- #
def getNewSourceIds():
    try:
        newSourceIdsUrl = baseApiUrl + '/newIds'
        newSourceIds = requests.get(newSourceIdsUrl, headers=apiHeaders).json()
        return newSourceIds
    except:
        print("COULDN'T POST PLAYERS NOT ON ROSTERS")

def postNewIds(newIdArr):
    if len(newIdArr) > 0:
        postNewIdsUrl = baseApiUrl + "/newIds"
        postResponse = requests.post(postNewIdsUrl, headers=apiHeaders, data=json.dumps(newIdArr))
        return postResponse.json()
    else:
        return "NO NEW IDS IN ARR"

# update current players w/ new source ids
def updatePlayerSourceIds(updates):
    for playerId, newSourceIds in updates.items():
        updatePlayerSourceIdUrl = baseApiUrl + '/players/' + str(playerId) + '/sourceIds'
        try:
            response = requests.put(updatePlayerSourceIdUrl, headers=apiHeaders, data=json.dumps(newSourceIds))
        except:
            print("COULDN'T UPDATE ", str(playerId))
            continue

# ---- GAMES ---- #
def getTodaysGames():
    # NOTE: This needs to be in PST
    DATE_FORMAT = '%Y-%m-%d'
    utc_date = datetime.now(tz=pytz.utc)
    pst_date = utc_date.astimezone(timezone('US/Pacific')).strftime(DATE_FORMAT)
    getGamesUrl = baseApiUrl + "/games?game_date=" + pst_date
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

def postGameSpreads(spreads):
    if len(spreads) > 0:
        postSpreadsUrl = baseApiUrl + "/games/lines"
        postResponse = requests.post(postSpreadsUrl, headers=apiHeaders, data=json.dumps(spreads))
        return postResponse.json()
    else:
        return "NO SPREADS IN ARR"

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
    if len(statsArr) > 0:
        postStatsUrl = baseApiUrl + "/stats"
        postResponse = requests.post(postStatsUrl, headers=apiHeaders, data=json.dumps(statsArr))

# --- POST GAME DATA --- #
def updateGamesWithPostgameData(postgameDataArr):

    if len(postGameData) > 0:
        for postGameData in postgameDataArr:
            postgameUpdateUrl = baseApiUrl + "/games/" + str(game["gameId"])
            gameUpdateResponse = requests.put(postgameUpdateUrl, headers=apiHeaders, data=json.dumps(postGameData))

        return "DONE"

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
    if len(predictionArr) == 0:
        print("NO PREDICTIONS TO POST, BLOCK API CALL")
        return None

    postPredictionsUrl = baseApiUrl + '/predictions'

    body = {
        'source': predSrc,
        'gameDate': gameDate,
        'statType': statType,
        'predictions': predictionArr
    }

    postResponse = requests.post(postPredictionsUrl, headers=apiHeaders, data=json.dumps(body))

    return postResponse

# --- SALARY DATA --- #
def postSalaries(salaries):
    '''
    salaries = array of salary objects w/ playerId, site, gameId, salary
    '''
    postPredictionsUrl = baseApiUrl + '/salaries'

    body = salaries

    postResponse = requests.post(postPredictionsUrl, headers=apiHeaders, data=json.dumps(body))

    return postResponse.json()

# -- ANALYTICS --- #
# def getPredictionsVsActual():




