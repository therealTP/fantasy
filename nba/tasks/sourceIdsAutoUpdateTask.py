import nba.ops.playerOps as pl
import nba.ops.apiCalls as api
import nba.ops.logger as logger 

try:
    pl.updatePlayerSourceIdsAutoAndLog()
    
except Exception as e:
    print("COULDN'T AUTO UPDATE PLAYER SOURCE IDS")