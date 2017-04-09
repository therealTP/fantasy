import json
import logging, logging.config
import loggly.handlers
from nba.ops.config import APP_CONFIG

config = APP_CONFIG

# import loggly config
logging.config.dictConfig(config["LOGGLY"])
logger = logging.getLogger('root')

def testLog():
    logger.info('Test test test')

# generic api error
def logApiError(call):
    logger.error('API call failed, status code not 200. Call: ' + str(call))

# -- PROJECTION SCRAPE LOGS -- #
def logProjectionScrapeSuccess(projectionDict, timeToRun):
    logger.info('Projections successfully scraped. Count: ' + str(len(projectionDict)) + '. Seconds to execute: ' + str(timeToRun))

def logProjectionScrapeError(errorMsg, timeToRun):
    logger.error('Scrape projections failed. Message: ' + str(errorMsg) + '. Seconds ran: ' + str(timeToRun))

# -- PLAYER UPDATE LOGS -- #
def logPlayerUpdateSuccess(playerUpdateDict, newPlayerData, playerNotOnRosterArr):
    message = {
        "Players Updated": len(playerUpdateDict),
        "New Complete Players Added": len(newPlayerData["complete"]),
        "New Incomplete Players Added": len(newPlayerData["incomplete"]),
        "Number players not on roster": len(playerNotOnRosterArr)
    }

    logger.info('Player statuses successfully updated. Details: ' + str(message))

def logPlayerUpdateError(error):
    logger.error('Failed to complete player update task. Error: ' + str(error))

def logSourceIdsUpdate(sourceIds, method):
    logger.info('New player source IDs updated. Players updated: ' + str(len(sourceIds)) + ". Method: " + method)

def logIncompletePlayersUpdate(playerBios):
    logger.info('Incomplete players updated. Players updated: ' + str(len(playerBios)))

# -- ACTUAL STATS LOGS --- #
def logActualStatsError(error):
    logger.error('Failed to retrieve or post actual stats. Error:', error)

# -- ML LOGS -- #
def logRetrainGoogleModelSuccess(stat, newNumEntries):
    logger.info('Google model for ' + str(stat) + ' retrained. Number entries: ' + str(newNumEntries))

# -- GAME SPREAD LOGS -- #
def logSpreadScrapeSuccess(spreads):
    logger.info('Game spreads successfully scraped for ', len(spreads), ' games.')

def logSpreadScrapeError(error):
    logger.error('Failed to complete scrape spreads task. Error: ' + str(error))

# -- TASK LOGS --- #
def logFirstOfDayUpdateError(error):
    logger.error('Failed to complete initial daily task. Error: ' + str(error))

def logSalaryScrapeTaskSuccess(salaries):
    logger.info('Salary data scraped. # salaries: ' + str(len(salaries)))

def logSalaryScrapeTaskError(error):
    logger.error('Failed to complete scrape salary task. Error: ' + str(error))





