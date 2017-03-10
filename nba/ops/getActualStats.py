import requests

import nba.scrapers.game_stats_scraper as gs
import nba.ops.apiCalls as api 

def scrapeGameStats(gameOrMinDate, maxDate=None):
    
    if maxDate == None:
        gamesToScrape = api.getGamesForDate(gameOrMinDate)
    else:
        gamesToScrape = api.getGamesInRange(gameOrMinDate, maxDate)

    playerList = api.getCurrentPlayerData()
    session = requests.Session()

    allGameStats = []

    for game in gamesToScrape:
        statsForGame = gs.getGameStats(game, playerList, session)
        allGameStats.extend(statsForGame)

    return allGameStats
        
    
    