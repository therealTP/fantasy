import json
import logging, logging.config
import loggly.handlers

with open('./../config.json') as config_file:
    config = json.load(config_file)

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
    logger.error('Scrape projections failed. Message: ' + errorMsg + '. Seconds ran: ' + timeToRun)

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
    logger.error('Failed to complete player update task. Error: ' + error)



