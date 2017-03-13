import nba.ops.scrapeProjections as sc
import nba.ops.apiCalls as api
import nba.ops.logger as logger
import nba.ops.notifyOps as notify
import time 

startTime = time.time()

try:
    rawProjHtml = sc.getAllRawHtml()
    projectionDict = sc.parseProjsFromHtml(rawProjHtml)
    # print(projectionDict["counts"])

    postProjsResponse = api.postProjections(projectionDict["projections"])
    newIdsResponse = api.postNewIds(projectionDict["newPlayerIds"])

    endTime = time.time()
    timeToRun = endTime - startTime
    notify.notifyProjectionScrapeSuccess(projectionDict["counts"], timeToRun)
    logger.logProjectionScrapeSuccess(projectionDict, timeToRun)
    
except Exception as error:
    endTime = time.time()
    timeToRun = endTime - startTime
    notify.notifyProjectionScrapeError(error)
    logger.logProjectionScrapeError(error, timeToRun)



