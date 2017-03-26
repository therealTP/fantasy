import requests
from datetime import datetime, timedelta, date
import pytz
from pytz import timezone

import nba.scrapers.actual_stats_scraper as actual
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
        statsForGame = actual.getGameStats(game, playerList, session)
        allGameStats.extend(statsForGame)

    return allGameStats

def scrapeActualGameStatsForYesterdayAndPostToDb():
    DATE_FORMAT = '%Y-%m-%d'
    yesterday_utc = datetime.now(tz=pytz.utc) - timedelta(days=1)
    yesterday_pst = yesterday_utc.astimezone(timezone('US/Pacific')).strftime(DATE_FORMAT)

    stats = scrapeGameStats(yesterday_pst)
    return api.postActualStats(stats)
        
    
    