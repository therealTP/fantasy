import nba_gamelog_scraper as nba
import s3
import json
import os
import DataSuite as ds
import linksFilesCreds as lfc

# # get yesterday's date
# yest = ds.getYesterdayDate()
#
# # get all actual game stats for yesterday
# stats = nba.getStatsForDate(yest)

# get all dates in range
dates_to_scrape = ds.getDateRangeArr('2015-11-02', '2016-04-05')

# get stats for each game date
all_stats = nba.getStatsForDateArr(dates_to_scrape)

for date, stats in all_stats.items():

    num_entries = len(stats)

    # create json filename
    json_file = date + '_actual.json'

    # write yesterday's stats to json
    with open(json_file, 'w') as f:
        json.dump(stats, f)

    # put json to s3 bucket
    s3_result = s3.putObjectS3(json_file, lfc.AWS_BUCKET_NAME, lfc.STATS_FOLDER)

    # remove file
    os.remove(json_file)

    # print messages for logs
    print (str(num_entries) + " actual entries scraped for " + date)
    print ('S3 put successful: ' + str(s3_result))
