import requests
import json
from lxml import html

from nba.classes.NbaPlayerStat import NbaPlayerStat
from nba.ops.config import APP_CONFIG

config = APP_CONFIG

def getStatForRow(row, gameId, teamId, playerList):

    brefId = row.cssselect('th:first-child a')[0].get('href').split('/')[3].replace('.html', '')
    playerObj = next((player for player in playerList if player["bref_id"] == brefId), None)
    
    # if no match for player's bref ID, return none
    if playerObj is None:
        return None
    else:
        # array of content of first cell
        time_array = row[1].text_content().split(':')

        try:
            raw_mins = float(time_array[0])
            sec_in_decimal = int(time_array[1]) / 60
            mins = round(raw_mins + sec_in_decimal, 2)

            # get all relevant stats
            pts = int(row[19].text_content())
            reb = int(row[13].text_content())
            ast = int(row[14].text_content())
            stl = int(row[15].text_content())
            blk = int(row[16].text_content())
            tpt = int(row[5].text_content())
            tov = int(row[17].text_content())

            stat = NbaPlayerStat(playerObj["player_id"], gameId, teamId, mins, pts, reb, ast, stl, blk, tpt, tov)
            return stat.__dict__
        # if value error is thrown, player usually did not player w/ status of DNP, DID NOT DRESS, etc.
        except ValueError:
            return None

def getGameStats(gameData, playerList, sessionObj):
    print("GETTING ACTUAL STATS FOR ", gameData["bref_slug"])
    gameUrl = config["BREF_GAME_BASE_URL"] + gameData["bref_slug"] + ".html"
    gameId = gameData["game_id"]
    page = sessionObj.get(gameUrl)
    tree = html.fromstring(page.text)
    gameStats = []

    tables = tree.cssselect('table.stats_table')

    awayTable = tables[0]
    awayStatRows = awayTable.cssselect('tbody tr:not(.thead)')

    for awayPlayer in awayStatRows:
        awayPlayerStat = getStatForRow(awayPlayer, gameId, gameData["away_team_id"], playerList)
        if awayPlayerStat is None:
            continue
        else:
            gameStats.append(awayPlayerStat)

    homeTable = tables[2]
    homeStatRows = homeTable.cssselect('tbody tr:not(.thead)')
    
    for homePlayer in homeStatRows:
        homePlayerStat = getStatForRow(homePlayer, gameId, gameData["home_team_id"], playerList)
        if homePlayerStat is None:
            continue
        else:
            gameStats.append(homePlayerStat)

    return gameStats



