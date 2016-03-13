import requests
import re
import json
import DataSuite as ds
import linksFilesCreds as lfc
import PlayerSuite as ps

"""
NUMBERFIRE
"""

URL = lfc.NF_SCRAPE_URL
AUTH = lfc.NF_CREDS


def getRawData(url, creds):
    """
    Takes in scrape_url, creds, search param
    Returns raw data in json format
    """

    # use requests module to hit URL
    r = requests.get(url, auth=creds)

    # get raw html from url
    raw_html = r.text

    # search raw html for re paramter to get raw data
    raw_data = re.search("NF_DATA = (.*)}}};", raw_html)

    # convert raw data to json data
    json_data = json.loads((raw_data.group(1)) + "}}}")

    return json_data


def extractProjectedStats(json_data):

    projection_dict = {}

    for item in json_data["daily_projections"]:

        # get nf stats
        source_id = item["nba_player_id"]

        # create dict entry for player stats
        entry = ds.createEntry(item["pts"], item["treb"],
                                    item["ast"], item["stl"],
                                    item["blk"], item["tov"],
                                    item["p3m"], item["minutes"])

        # get name from player dict
        name = json_data["players"][source_id]["name"]

        # look up or generate universal id for player
        player_id = ps.getPlayerId(source_id, 1, name)

        # if no player id:
        if player_id is None:
            # pass on data entry, do not add proj data for this player
            pass
            # entry for the unfound id added to queue

        ds.addEntryToProjectionDict(projection_dict, player_id, entry)

    return projection_dict


def extractPlayerData(json_data):
    """
    used for updating master player list
    extracts player data from raw data
    """

    # json_data = getRawData(URL, AUTH)
    player_data = json_data['players']

    return player_data


def updatePlayerList(player_data):

    for player_id, data in player_data.items():
        name = data["name"]
        player_id = ps.getPlayerId(player_id, 1, name)
