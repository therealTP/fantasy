###
# This task is ran once at the beginning of the day to get all data from yesterday
# Will provide main updates of injuries, depth charts, etc.
###
import requests
import nba.ops.playerOps as pl
import nba.ops.apiCalls as api
import nba.ops.logger as logger
import nba.ops.notifyOps as notify
import nba.ops.actualStatsOps as actual 

try:
    # get all current player data
    pl.updateAllPlayerDataAndLog()
    # auto update any source ids added from yesterday's projections
    pl.updatePlayerSourceIdsAutoAndLog()
    # get a count of how many manual updates are pending in the db (for notification)
    manualUpdates = api.getPendingManualUpdatesCounts()
    # get actual player stats from yesterday's games
    actual.scrapeActualGameStatsForYesterdayAndPostToDb()

    # TODO: get post game data, e.g scores, injuries, winner, etc
    # actual.getYesterdayPostGameDataAndPostToDb()

    # TODO: retrain models w/ yesterday's data
    # google.retrainAllModelsWithYesterdaysData()

    notify.notifyFirstOfDayUpdateTaskSuccess(manualUpdates)

except Exception as error:
    # log error:
    logger.logFirstOfDayUpdateError(error)

    # notify error
    notify.notifyFirstDayOfUpdateError(error)
