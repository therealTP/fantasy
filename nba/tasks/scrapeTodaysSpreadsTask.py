###
# This task will be run right before predictions are pulled/posted 
# Used in predictions for optimal lineup
###

import nba.ops.logger as logger
import nba.ops.notifyOps as notify
import nba.ops.spreadOps as spread 

try:
    spreads = spread.getSpreadsForTodayAndPostToApi()
    notify.notifySpreadsScrapeSuccess(spreads)

    # no log required here - will happen in salaryOps

except Exception as error:
    # log error:
    logger.logSpreadScrapeError(error)

    # notify error
    notify.notifySpreadsScrapeError(error)
