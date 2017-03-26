import json
import requests
from nba.scrapers.game_data_scraper import getAllGames
from nba.ops.config import APP_CONFIG

config = APP_CONFIG

# constants
YEAR = 2017
MONTHS = ['october', 'november', 'december', 'january', 'february', 'march', 'april']
BASE_URL = 'http://www.basketball-reference.com/leagues/NBA_' + str(YEAR) + '_games-'
URL_EXT = '.html'
TABLE_ID = '#schedule'

# start session
session = requests.Session()

# get all games
allGames = getAllGames(session, MONTHS, BASE_URL, URL_EXT, TABLE_ID)

# --- POST TO API --- #
apiHeaders = {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + config["API_TOKEN"]
}

baseApiUrl = config["API_URL"] + ":" + str(config["API_PORT"])
postBody = json.dumps({
    "games": allGames
})

# POST game data to API
postGamesUrl = baseApiUrl + "/games"
postRes = requests.post(postGamesUrl, data=postBody, headers=apiHeaders).json()

print("POST RES", postRes)