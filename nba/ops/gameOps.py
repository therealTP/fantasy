import requests
import json
import csv
from datetime import datetime, timedelta, date
import pytz

import nba.scrapers.post_game_scraper as post
import nba.ops.mlDataPrep as ml
import nba.ops.apiCalls as api 

def getYesterdaysGames():
    DATE_FORMAT = '%Y-%m-%d'
    yesterday_utc = datetime.now(tz=pytz.utc) - timedelta(days=1)
    yesterday_pst = yesterday_utc.astimezone(pytz.timezone('US/Pacific')).strftime(DATE_FORMAT)

    return api.getGamesForDate(yesterday_pst)

def getGamesForDateRange(startDate, endDate):
    dateArr = ml.getDateRangeArr(startDate, endDate)

    allGames = []

    for date in dateArr:
        games = api.getGamesForDate(date)
        allGames.extend(games)

    return allGames

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

def getPostGameDataForGameArr(game_arr):
    all_post_game_data = []

    player_data = api.getCurrentPlayerData()
    session = requests.Session()

    for game in game_arr:
        post_game_data = post.getBoxScoreData(game["bref_slug"], session, player_data)
        post_game_data["gameId"] = game["game_id"]
        all_post_game_data.append(post_game_data)

    return all_post_game_data

def getPostGameDataForDateRangeAndPostToApi(startDate, endDate):
    games = getGamesForDateRange(startDate, endDate)
    postGameData = getPostGameDataForGameArr(games)
    apiRes = api.updateGamesWithPostgameData(postGameData)

    return apiRes


