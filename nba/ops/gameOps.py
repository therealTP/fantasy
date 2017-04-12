import requests
import json
import csv
from datetime import datetime, timedelta, date
import pytz

import nba.scrapers.post_game_scraper as post
import nba.ops.apiCalls as api 

def getYesterdaysGames():
    DATE_FORMAT = '%Y-%m-%d'
    yesterday_utc = datetime.now(tz=pytz.utc) - timedelta(days=1)
    yesterday_pst = yesterday_utc.astimezone(pytz.timezone('US/Pacific')).strftime(DATE_FORMAT)

    return api.getGamesForDate(yesterday_pst)

def getPostGameDataForYesterdaysGames():
    games = getYesterdaysGames()

    playerData = api.getCurrentPlayerData()
    session = requests.Session()

    allPostGameData = []

    for game in games:
        print(game["bref_slug"])
        postGameData = post.getBoxScoreData(game["bref_slug"], session, playerData)
        allPostGameData.append(postGameData)

    return allPostGameData

# def getGameLinesForTodaysGames():