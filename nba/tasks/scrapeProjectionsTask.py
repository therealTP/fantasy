import nba.ops.scrapeProjections as sc
import nba.ops.apiCalls as api
import nba.ops.logger as logger
import time 

startTime = time.time()

try:
    rawProjHtml = sc.getAllRawHtml()
    projectionDict = sc.parseProjsFromHtml(rawProjHtml)
    print(projectionDict)

    # api.postProjections(projectionDict["projections"])
    # api.postNewIds(projectionDict["newPlayerIds"])

    endTime = time.time()
    timeToRun = endTime - startTime
    logger.logProjectionScrapeSuccess(projectionDict, timeToRun)
    
except Exception as error:
    endTime = time.time()
    timeToRun = endTime - startTime
    logger.logProjectionScrapeError(error, timeToRun)



