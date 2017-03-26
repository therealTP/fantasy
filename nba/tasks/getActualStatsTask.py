###
# ONE OFF: used for getting actual game stats for a period
# of time, i.e. date range
###

from nba.ops.getActualStats import scrapeGameStats
import nba.ops.apiCalls as api

try:
    # first param is start date of game range OR only date, 2nd is end date (optional)
    stats = scrapeGameStats('2016-01-02', '2016-05-01')
    api.postActualStats(stats)
except Exception as e:
    print("ERROR", e)