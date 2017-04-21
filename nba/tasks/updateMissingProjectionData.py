import requests
from lxml import html

import nba.ops.csvOps as csvOps
import nba.ops.apiCalls as api
import nba.ops.jsonData as jsonData

def getMissingData():

    filename = "missing_player_data.csv"
    fileLoc = jsonData.LOCAL_DATA_PATH + filename
    rows = csvOps.openCsvFromFileToArrays(fileLoc)
    gamesForSeason = api.getGamesInRange('2015-11-01', '2016-04-13')
    teamDict = jsonData.TEAM_ABBREV_TO_ID

    session = requests.Session()

    matchedData = []
    missingData = []
    toDelete = []

    for player in rows:
        playerId = player[0]
        brefId = player[1]
        missingDates = player[2].split(",")

        baseUrl = "http://www.basketball-reference.com/players/"
        firstLetter = brefId[0] + "/"
        endUrl = "/gamelog/2016/"

        fullUrl = baseUrl + firstLetter + brefId + endUrl
        
        rawHtml = session.get(fullUrl).content
        tree = html.fromstring(rawHtml)
        games = tree.cssselect('table#pgl_basic tbody tr:not(.thead)')
        totalGamesInSeason = len(games)

        # check for matching games, removing dates if they match:
        for game in games:
            gameDate = game[2].text_content().strip()
            teamId = teamDict[game[4].text_content().strip()]
            
            # check if matching game date found for missing date
            if gameDate in missingDates:
                gameBref = game[2].cssselect('a')[0].get('href').split("/")[-1].replace(".html", "")
                game = next((game for game in gamesForSeason if game["bref_slug"] == gameBref), None)
                missingDates.remove(gameDate)

                if game is None:
                    print("NO GAME MATCH", gameDate, str(missingDates), brefId)
                    continue

                dataRow = [playerId, gameDate, teamId, game["game_id"]]
                matchedData.append(dataRow)
        
        # for any leftover missing dates:
        for gameDate in missingDates:
            missingData.append([playerId, brefId, gameDate])

    csvOps.writeToCsv(matchedData, jsonData.LOCAL_DATA_PATH + "matched-data.csv")

getMissingData()