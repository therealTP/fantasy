'''
This task will be run manually, as needed to match bref id to incomplete player entries &
Pull their bio data
For players that couldn't be matched by exact name
'''
import requests
import nba.ops.playerOps as pl
import nba.ops.apiCalls as api

try:
    # 1. Update incomplete players
    pl.manualUpdateIncompletePlayersAndLog()

    # 2. update source ids w/ no auto name match
    pl.updateSourceIdsForPlayersManualAndLog()
except Exception as error:
    print(error)
    # don't need to log, it's manual
