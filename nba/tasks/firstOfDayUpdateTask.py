###
# This task is ran once at the beginning of the day to get all data from yesterday
# Will get actual stats, game data, and retrain all models w/ that data
###
import requests
import nba.ops.playerOps as pl
import nba.ops.apiCalls as api
import nba.ops.logger as logger
import nba.ops.notifyOps as notify
import nba.ops.actualStatsOps as actual 
import nba.ops.gameOps as game

try:
    # get actual player stats from yesterday's games
    actual.scrapeActualGameStatsForYesterdayAndPostToDb()

    # TODO: retrain models w/ yesterday's data
    # google.retrainAllModelsWithYesterdaysData()

    # get all postgame data (BEFORE PLAYER UPDATE, for injuries)
    # TODO: get DNP/ 0 minutes & injuries/inactive

    # get all current player data
    pl.updateAllPlayerDataAndLog()
    # auto update any source ids added from yesterday's projections
    pl.updatePlayerSourceIdsAutoAndLog()
    # get a count of how many manual updates are pending in the db (for notification)
    manualUpdates = api.getPendingManualUpdatesCounts()

    # TODO: get post game data, e.g scores, injuries, winner, etc
    # actual.getYesterdayPostGameDataAndPostToDb()

    notify.notifyFirstOfDayUpdateTaskSuccess(manualUpdates)

except Exception as error:
    # log error:
    logger.logFirstOfDayUpdateError(error)

    # notify error
    notify.notifyFirstDayOfUpdateError(error)
