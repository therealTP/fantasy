import arrow
import requests
import json
import os
import s3
from lxml import html
import PlayerSuite as ps
import DataSuite as ds
import linksFilesCreds as lfc

def getDateRangeArr(startDate, endDate):
    """
    Date arguments in YYYY-MM-DD format
    Inclusive of dates entered
    Dates in arr also in YYYY-MM-DD format
    """
    # convert date strings to arrow objects
    startArrow = arrow.Arrow.strptime(startDate, '%Y-%m-%d')
    endArrow = arrow.Arrow.strptime(endDate, '%Y-%m-%d')

    datesArr = []

    # loop through range between start & end
    while (startArrow <= endArrow):
        # add each date to datesArr
        datesArr.append(startArrow.format('YYYY-MM-DD'))
        # increment start by a day
        startArrow = startArrow.replace(days=+1)

    return datesArr

def getFcDataForDates(datesArr, site):
    """
    Takes in array of YYYY-MM-DD format date strings
    Each date string is used to build url
    Scrapes/parses data from each URL & updates to S3 obj
    """
    salaries = {}
    projections = {}

    with requests.Session() as c:
        for date in datesArr:
            url = lfc.FC_BASE_URL + site + '/NBA/' + date
            page = c.get(url, headers=lfc.BR_HEADER)
            # print(page.text)
            tree = html.fromstring(page.text)
            rows = tree.cssselect('table#ff tbody tr')
            salariesForDate = {}
            projectionsForDate = {}

            # will not go through this loop if the table has no data rows
            for row in rows:
                fcPlayerId = row.get('data-playerid')
                name = row[0].cssselect('span.player-stats')[0].text_content()
                pos = row[1].text_content()
                salary = row[5].text_content().strip()
                mins = row[9].text_content()
                proj = row[10].text_content()
                playerId = ps.getPlayerId(fcPlayerId, 6, name, pos)

                # print(salary, mins, proj)

                salariesForDate[playerId] = {}
                salariesForDate[playerId][site] = salary
                projectionsForDate[playerId] = proj

            salaries[date] = salariesForDate
            projections[date] = projectionsForDate
            print("salary & proj data scraped for ", date)

    return [salaries, projections]

datesArr = getDateRangeArr('2015-11-02', '2016-03-29')
fcData = getFcDataForDates(datesArr, 'draftkings')

# create file name from today's date, inc. data folder
salary_json_file = "salaries.json"
proj_json_file = "fc_projections.json"

# write final data_dict to json file w/ file name
with open(salary_json_file, 'w') as write_json:
    json.dump(fcData[0], write_json)

with open(proj_json_file, 'w') as write_json:
    json.dump(fcData[1], write_json)

# put json file to s3 bucket
s3_result_salary = s3.putObjectS3(salary_json_file, lfc.AWS_BUCKET_NAME, lfc.SALARIES_FOLDER)
s3_result_proj = s3.putObjectS3(proj_json_file, lfc.AWS_BUCKET_NAME, lfc.PROJECTIONS_FOLDER)

# delete json_file from local storage (s3 put complete)
os.remove(salary_json_file)
os.remove(proj_json_file)
