'''
This task is run continuously, starting an hr before the game.
Will provide main updates of injuries, depth charts, etc.
'''
import requests
import nba.ops.playerUpdate as pl
import nba.ops.apiCalls as api
import nba.ops.logger as logger
import nba.ops.notifyOps as notify 

try:
    pl.updateAllPlayerDataAndLog()
    pl.updatePlayerSourceIdsAutoAndLog()
    # TODO: get post game data
    # game.getYesterdaysGameDataAndPostToDb()

    manualUpdates = api.getPendingManualUpdatesCounts()
    notify.notifyFirstOfDayUpdateTaskSuccess(manualUpdates)

except Exception as error:
    # log error:
    logger.logFirstOfDayUpdateError(error)

    # notify error
    notify.notifyFirstDayOfUpdateError(error)
