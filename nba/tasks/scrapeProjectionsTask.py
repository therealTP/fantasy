import nba.ops.scrapeProjections as sc
import nba.ops.apiCalls as api
import nba.ops.logger as logger
import time 

startTime = time.time()

try:
    rawProjHtml = sc.getAllRawHtml()
    projectionDict = sc.parseProjsFromHtml(rawProjHtml)
    print(projectionDict["counts"])

    api.postProjections(projectionDict["projections"])
    newIdsResponse = api.postNewIds(projectionDict["newPlayerIds"])
    # print(newIdsResponse.json())

    endTime = time.time()
    timeToRun = endTime - startTime
    print("TIME", timeToRun)
    # logger.logProjectionScrapeSuccess(projectionDict, timeToRun)
    
except Exception as error:
    endTime = time.time()
    timeToRun = endTime - startTime
    # logger.logProjectionScrapeError(error, timeToRun)



