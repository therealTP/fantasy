import requests
import json
from lxml import html

from nba.classes.NbaPlayerStat import NbaPlayerStat
from nba.ops.config import APP_CONFIG

import nba.ops.apiCalls as api
import nba.ops.csvOps as csvOps

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


def get_usual_depth_positions(season):
    session = requests.Session()
    current_players = api.getCurrentPlayerData()
    # teams_url = 'http://www.basketball-reference.com/leagues/NBA_' + str(season) + '.html'
    depth_url = 'http://basketball.realgm.com/nba/depth-charts/' + str(season)

    page = session.get(depth_url)
    tree = html.fromstring(page.text)
    # team_rows = tree.cssselect('table#confs_standings_E tbody tr th a, table#confs_standings_W tbody tr th a')
    team_section = tree.cssselect('table.basketball tbody')

    all_depth_pos = {}

    for section in team_section:
        rows = section.cssselect('tr')
        for depth, row in enumerate(rows):
            players = row.cssselect("td.depth-chart-cell a")
            for player in players:
                player_name = " ".join(player.get("href").split("/")[2].split("-")).strip()
                player_obj = next((player for player in current_players if player["player_name"] == player_name), None)
                player_depth = depth + 1

                if player_obj is None:
                    player_id = int(input("What is the player_id for " + player_name + "? "))
                    if player_id == 0:
                        continue
                else:
                    player_id = player_obj["player_id"]

                if player_id in all_depth_pos:
                    if all_depth_pos[player_id] < player_depth:
                        all_depth_pos[player_id] = player_depth
                else:
                    all_depth_pos[player_id] = player_depth

    depth_rows = []
    filename = './../local-data/usual_depth_pos_2017.csv'
    for player, depth in all_depth_pos.items():
        depth_rows.append([player, depth])

    csvOps.writeToCsv(depth_rows, filename)

get_usual_depth_positions(2017)






