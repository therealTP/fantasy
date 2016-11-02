import requests
import json

# import config file
with open('./../config.json') as config_file:
    config = json.load(config_file)

# create new requests session
# session = requests.Session()

apiHeaders = {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + config["API_TOKEN"]
}

baseApiUrl = config["API_URL"] + ":" + str(config["API_PORT"])

# GET current player data from db
getPlayersUrl = baseApiUrl + "/players"
players = requests.get(getPlayersUrl, headers=apiHeaders)
print(players.json())

# scrape current depth chart data & starting lineup data from rw 

# break out data into current players and new players (use player data from db)

# PUT update current players

# get other data about new players (bref_id, position, bref data, etc)

# POST add new players w/ depth & other data