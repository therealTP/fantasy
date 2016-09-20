import requests
import json
import csv
from lxml import html
from dateutil import parser
from nba.classes.NbaGamePre import NbaGamePre

def getTeamIdFromAbbrev(teamAbbrev, teamIdDict):

    # look up team id in dict from abbrev
    try:
        return teamIdDict[teamAbbrev]
    except KeyError:
        return teamIdDict[teamAbbrev[0:2]]

def parseGameTime(rawTime):
    cleanTime = parser.parse(rawTime).strftime('%-H%M')
    timeList = list(cleanTime)
    if timeList[2] == "3":
        timeList[2] = "5"

    return "".join(timeList)

def getTeamAbbrFromTd(tdElem):
    homeTeamLink = tdElem.cssselect('a')[0].get('href')
    teamAbbr = homeTeamLink.split('/')[2]
    return teamAbbr

def getGamesFromMonth(month, sesObj, teamIdDict):
    """
    Takes in month str and requests session object
    """
    monthUrl = BASE_URL + month + URL_EXT
    page = sesObj.get(monthUrl)
    tree = html.fromstring(page.text)
    selector = 'table' + TABLE_ID + ' tbody tr'
    gameRows = tree.cssselect(selector)

    games = []

    for gameRow in gameRows:
        rawDayDate = gameRow[0].text_content()
        day = rawDayDate[:3]
        rawDate = rawDayDate[4:]
        try:
            date = parser.parse(rawDate).strftime('%Y-%m-%d')
        except:
            break

        rawTime = gameRow[1].text_content()
        gameTime = parseGameTime(rawTime)

        awayTeamAbbr = getTeamAbbrFromTd(gameRow[2])
        homeTeamAbbr = getTeamAbbrFromTd(gameRow[4])

        awayTeamId = getTeamIdFromAbbrev(homeTeamAbbr, teamIdDict)
        homeTeamId = getTeamIdFromAbbrev(awayTeamAbbr, teamIdDict)

        gameObj = NbaGamePre(date, day, gameTime, homeTeamId, awayTeamId)
        games.append(gameObj.getCsvRow())
    
    return games

def getAllGames(sessionObj, monthArr, teamIdDict):
    allGames = []
    for month in monthArr:
        print("SCRAPING", month)
        monthGames = getGamesFromMonth(month, sessionObj, teamIdDict)
        allGames.extend(monthGames)

    print("Games scraped:", len(allGames))
    
    return allGames

# constants
BASE_URL = 'http://www.basketball-reference.com/leagues/NBA_2016_games-'
URL_EXT = '.html'
MONTHS = ['october', 'november', 'december', 'january', 'february', 'march', 'april']
TABLE_ID = '#schedule'

# import team json as dict
with open('./../local-data/team-abbrev-to-id.json') as data_file:    
    teamIdDict = json.load(data_file)

# start session
session = requests.Session()

# get all games
allGames = getAllGames(session, MONTHS, teamIdDict)

# write all games to csv
with open('./../local-data/games.csv', 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter=",")
    writer.writerows(allGames)


# print(getTeamIdFromAbbrev('SAS'))










