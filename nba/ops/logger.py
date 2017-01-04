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

def logProjectionScrapeSuccess(projectionDict, timeToRun):
    logger.info('Projections successfully scraped. Count: ' + str(len(projectionDict)) + '. Seconds to execute: ' + str(timeToRun))

def logProjectionScrapeError(errorMsg, timeToRun):
    logger.error('Scrape projections failed. Message: ' + errorMsg + '. Seconds ran: ' + timeToRun)
