import datetime
import requests
import json

with open('./../config.json') as config_file:
    config = json.load(config_file)

apiHeaders = {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + config["API_TOKEN"]
}

baseApiUrl = config["API_URL"] + ":" + str(config["API_PORT"])

yesterday = datetime.datetime.strftime(datetime.datetime.now()-datetime.timedelta(1),'%Y-%m-%d')

def getGameDataFromDb(gameOrMinDate, maxDate=None):

    if maxDate != None:
        getGamesUrl = baseApiUrl + "/games?min_date=" + gameOrMinDate + "&max_date=" + maxDate
    else:
        getGamesUrl = baseApiUrl + "/games?game_date=" + gameOrMinDate
            
    playerData = requests.get(getGamesUrl, headers=apiHeaders).json()

    return playerData

# print(getGameDataFromDb(yesterday))
print(getGameDataFromDb('2015-10-01', '2016-05-01'))

# 1. get results of games, e.g. scores, who won, attendance, final injuries/DNP/etc.

# 2. get individual player stats for games

# 3. PUT/POST game results & player stats to API