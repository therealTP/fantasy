import nba.ops.playerOps as pl
import nba.ops.apiCalls as api
import nba.ops.logger as logger 

try:
    # get all new source ids
    sourceIdUpdates = pl.getSourceIdUpdatesForPlayersAuto()

    # make source id updates
    api.updatePlayerSourceIds(sourceIdUpdates)
    
except Exception as e:
    print("COULDN'T AUTO UPDATE PLAYER SOURCE IDS")