'''
This task will be run manually, as needed to match bref id to incomplete player entries &
Pull their bio data
For players that couldn't be matched by exact name
'''
import requests
import nba.ops.playerUpdate as pl
import nba.ops.apiCalls as api

try:
    # create new requests session
    session = requests.Session()

    # 1. Update incomplete players
    # get all incomplete players
    incompletePlayers = api.getIncompletePlayers()

    # get bio data for all incomplete players (manually enter brefIds)
    playerBios = pl.getBiosForIncompletePlayers(session, incompletePlayers)

    # make api call to update those players
    api.updatePlayerBios(playerBios)

    # TODO: 2. update source ids w/ no auto name match
    
    # TODO: log players & source ids updated
except Exception as error:
    print(error)
    # TODO: log couldn't update players
