import nba_gamelog_scraper as nba
import s3
import json
import os
import DataSuite as ds
import linksFilesCreds as lfc

# get yesterday's date
yest = ds.getYesterdayDate()

# get all actual game stats for yesterday
stats = nba.getStatsForDate(yest)

num_entries = len(stats)

# create json filename
json_file = yest + '_actual.json'

# write yesterday's stats to json
with open(json_file, 'w') as f:
    json.dump(stats, f)

# put json to s3 bucket
s3_result = s3.putObjectS3(json_file, lfc.AWS_BUCKET_NAME, lfc.STATS_FOLDER)

# remove file
os.remove(json_file)

# print messages for logs
print (str(num_entries) + " actual entries scraped for " + yest)
print ('S3 put successful: ' + str(s3_result))
