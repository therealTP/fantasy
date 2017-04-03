###
# This task ran once a day ~ noon PST, as salaries do not change 
###

import nba.ops.logger as logger
import nba.ops.notifyOps as notify
import nba.ops.salaryOps as salary 

try:
    numSalaries = salary.getSalariesForTodayAndPostToApi()
    notify.notifySalaryScrapeSuccess(numSalaries)

    # no log required here - will happen in salaryOps

except Exception as error:
    # log error:
    logger.logSalaryScrapeTaskError(error)

    # notify error
    notify.notifySalaryScrapeTask(error)
