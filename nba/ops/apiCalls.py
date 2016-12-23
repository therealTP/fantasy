import requests
import json

# import config file
with open('./../config.json') as config_file:
    config = json.load(config_file)

apiHeaders = {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + config["API_TOKEN"]
}

baseApiUrl = config["API_URL"] + ":" + str(config["API_PORT"])

# GET current player data from db
def getCurrentPlayerData():
    getPlayersUrl = baseApiUrl + "/players"
    playerData = requests.get(getPlayersUrl, headers=apiHeaders).json()
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