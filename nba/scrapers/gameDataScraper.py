import json
from lxml import html
from dateutil import parser
from nba.classes.NbaGamePre import NbaGamePre

# import team json as dict
with open('./../local-data/team-abbrev-to-id.json') as data_file:    
    teamIdDict = json.load(data_file)

def getTeamIdFromAbbrev(teamAbbrev):

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

    return int("".join(timeList))

def getTeamAbbrFromTd(tdElem):
    homeTeamLink = tdElem.cssselect('a')[0].get('href')
    teamAbbr = homeTeamLink.split('/')[2]
    return teamAbbr

def getGamesFromMonth(month, sesObj, baseUrl, urlExt, tableId):
    """
    Takes in month str and requests session object
    """
    monthUrl = baseUrl + month + urlExt
    page = sesObj.get(monthUrl)
    tree = html.fromstring(page.text)
    selector = 'table' + tableId + ' tbody tr'
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

        awayTeamId = getTeamIdFromAbbrev(awayTeamAbbr)
        homeTeamId = getTeamIdFromAbbrev(homeTeamAbbr)

        gameSlug = date + "_" + str(awayTeamId) + "_" + str(homeTeamId)

        gameObj = NbaGamePre(date, gameTime, day, awayTeamId, homeTeamId, gameSlug)
        games.append(gameObj.getCsvRow())
    
    return games

def getAllGames(sessionObj, monthArr, baseUrl, urlExt, tableId):
    allGames = []
    for month in monthArr:
        print("SCRAPING", month)
        monthGames = getGamesFromMonth(month, sessionObj, baseUrl, urlExt, tableId)
        allGames.extend(monthGames)

    print("Games scraped:", len(allGames))
    
    return allGames










