import nba.ops.playerUpdate as pl
import nba.ops.apiCalls as api
import nba.ops.logger as logger 

try:
    # get all new source ids
    sourceIdUpdates = pl.getSourceIdUpdatesForPlayersAuto()

    # make source id updates
    api.updatePlayerSourceIds(sourceIdUpdates)

    # TODO: delete the new source ids for players just added
    
except Exception as e:
    print("COULDN'T AUTO UPDATE PLAYER SOURCE IDS")