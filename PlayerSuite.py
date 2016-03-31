import json
import linksFilesCreds as lfc
from difflib import get_close_matches


def queueNewPlayer(player_name, id_key, player_id, position=None):
    """
    Adds new data to player_queue json for eval
    id_key = 'nf_id'/ 'rw_id'/ 'bm_id'/ etc.
    Also looks for names matches add includes w/ data
    """
    # create array to hold all current player names
    current_player_names = []

    # open player_data json into dict
    with open(lfc.PLAYER_DATA, 'r', encoding='utf-8') as data_file:
        player_dict = json.loads(data_file.read())

        # for each entry in dict
        for key, val in player_dict.items():
            # look up name of player
            name = val["name"]
            # add name to player_names array
            current_player_names.append(name)

    with open(lfc.PLAYER_QUEUE, 'r') as queue_json:
        queue_dict = json.loads(queue_json.read())

        # get closest matches (if any)
        matches = get_close_matches(player_name, current_player_names)

        # add new entry to queue dict for player
        queue_dict[player_name] = {"id_key": id_key, "player_id": player_id,
                                   "name_matches": matches}

        if position != None:
            queue_dict[player_name]["pos"] = position

    with open(lfc.PLAYER_QUEUE, 'w') as queue_json:
        json.dump(queue_dict, queue_json)


def getPlayerId(player_id, source_id, player_name, position=None):
    """
    lookup_param: name(str) or ID
    source id: single digit
    returns universal id from player dict
    position only comes from fantasy cruncher
    """

    # assign correct value for id_key based on source
    if source_id == 1:
        id_key = "nf_id"

    elif source_id == 2:
        id_key = "rw_id"

    elif source_id == 3:
        id_key = "bm_id"

    elif source_id == 4:
        id_key = "fp_id"

    elif source_id == 5:
        id_key = "bref_id"

    elif source_id == 6:
        id_key = "fc_id"

    else:
        return "You've entered an invalid source_id."

    # open player data json and convert to dict
    with open(lfc.PLAYER_DATA, encoding='utf-8') as data_file:
        player_json = json.loads(data_file.read())

    # loop through all players and check for matches (id or name)
    for key, val in player_json.items():

        # check to see if player id for source is present & matches
        if (id_key in val and val[id_key] == player_id):
            # if so, return universal player id
            return key

        # check for match for exact player name (case insensitive)
        elif val["name"].lower() == player_name.lower():
            # if so, add current source_id to data_dict
            val[id_key] = player_id
            # if positon argument included, add that as well
            if position != None:
                val["pos"] = position

            # update player_data file with player_id
            with open(lfc.PLAYER_DATA, 'w') as write_json:
                json.dump(player_json, write_json)

            # return key
            return key

    # if loop through current dict finds no matches:
    queueNewPlayer(player_name, id_key, player_id, position)
    print ("ID for " + player_name + " not found. Added to player queue.")
    return None


def addNewPlayerData(id_key, player_id, player_name, position=None):
    """
    id_key = "nf_id", "rw_id", "bm_id" etc.
    player id = id from source, name
    """

    with open(lfc.PLAYER_DATA, encoding='utf-8') as data_file:
        player_dict = json.loads(data_file.read())

        new_id = str(max([int(i) for i in player_dict.keys()]) + 1)

        player_dict[new_id] = {id_key: player_id, "name": player_name}

        if position != None:
            player_dict[new_id]["pos"] = position

    with open(lfc.PLAYER_DATA, 'w') as f:
        json.dump(player_dict, f)

    print ("New player entry added for " + player_name)


def updateExistingPlayer(player_name, id_key, player_id, position=None):
    """
    id_key = "nf_id", "rw_id", "bm_id" etc.
    player id = id from source, name
    """

    # open player data json and convert to dict
    with open(lfc.PLAYER_DATA, encoding='utf-8') as data_file:
        player_dict = json.loads(data_file.read())

    # loop through all players and check for matches (id or name)
    for key, val in player_dict.items():

        # check for match for exact player name
        if val["name"] == player_name:
            # if so, add current source_id to player_data
            val[id_key] = player_id
            # if a position is provided, include it in player update
            if position != None:
                val["pos"] = position
            break

    with open(lfc.PLAYER_DATA, 'w') as f:
        json.dump(player_dict, f)

    print ("Data updated for " + player_name)


def checkPlayerQueue():
    """
    Loops through each item in queue and asks what to do
    1: add new player/ 2: update current player/ 3: skip/ 4: delete
    """

    with open(lfc.PLAYER_QUEUE, encoding='utf-8') as queue_json:
        queue_dict = json.loads(queue_json.read())

        entries_to_delete = []

        for key, val in queue_dict.items():
            # pull values from entry
            name = key
            id_key = val["id_key"]
            player_id = val["player_id"]
            matches = val["name_matches"]
            try:
                position = val["pos"]
            except KeyError:
                position = None

            print (key + ": " + str(val))

            response = input('What to do with this entry? 1 to add new player, 2 to update existing, 3 to skip, 4 to delete entry.')

            # response 1: add new entry for player in player data
            if response == "1":
                addNewPlayerData(id_key, player_id, name, position)
                # add to entries to delete arr
                entries_to_delete.append(name)

            # 2: update an existing player
            elif response == "2":
                # prompt which current player is a match
                name_index = input("Which player (num)? " + str(matches))

                # get correct name to updated from matches array
                name_to_update = matches[int(name_index) - 1]

                # update chosen player with new data
                updateExistingPlayer(name_to_update, id_key, player_id, position)

                # add to entries to delete arr
                entries_to_delete.append(name)

            # 3: skip this entry
            elif response == "3":
                pass

            # 4: delete this entry
            elif response == "4":
                # add to entries to delete arr
                entries_to_delete.append(name)

            else:
                print ("You've entered an incorrect option.")

        # delete all entries from delete array
        for name in entries_to_delete:
            del queue_dict[name]

        # rewrite queue to json
        with open(lfc.PLAYER_QUEUE, 'w') as f:
            json.dump(queue_dict, f)


def getQueueCount():

    with open(lfc.PLAYER_QUEUE, encoding='utf-8') as queue_json:
        queue_dict = json.loads(queue_json.read())

        count = len(queue_dict)

        return count

def getPlayerList():
    with open(lfc.PLAYER_DATA, encoding='utf-8') as data_file:
        player_dict = json.loads(data_file.read())

        return player_dict
