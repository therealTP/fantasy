from datetime import datetime, timedelta
from statistics import mean
from math import sin, cos, sqrt, atan2, radians
import nba.ops.apiCalls as api
import nba.ops.csvOps as csv

def getColumns():
    columns = [
        # ACTUAL STAT OF TYPE (only included in training data)
        "actual_stat", 
        # PROJECTION DATA
        "nf", "rw", "bm", "fp",
        # PLAYER DATA
        "bref_id", "player_position", "depth_pos", "usual_depth_pos", "is_starter", 
        "height", "weight", "age", "exp_months",  "games_played", "draft_pick", "current_salary",
        # TEAM DATA
        "team_abbrev", "team_won_last_game", "team_winning_pct",
        # GAME DATA
        "is_home", "opponent_abbrev", "team_spread", "team_pred_pts", 
        # GAME TIME & DATE
        "game_time_24_et", "game_tz", "day_of_week", "game_month",
        # BASIC INJURY COUNT
        "num_teammates_injured", "num_opponents_injured",
        # STADIUM ATTENDANCE
        "stadium_avg_att", "avg_att_pct",
        # RECENT GAMES PLAYED
        "played_in_last_team_game", "won_last_game_played", "num_games_past_week",
        # MINS & STAT FOR LAST GAME & AVG OF LAST 5 & 10
        "mins_last_game", "avg_mins_last_five", "avg_mins_last_ten",
        "stat_last_game", "avg_stat_last_five", "avg_stat_last_ten",
        # TIME SINCE LAST GAME:
        "total_hrs_since_last_game", 
        # INDIVIDUAL STREAKS:
        "winning_streak", "losing_streak", "win_pct_last_five", "win_pct_last_ten",
        # DISTANCE TRAVELED:
        "distance_traveled_for_game", "distance_traveled_past_week",
        # TIMEZONES:
        "tz_change_for_game", "tz_change_past_week"
    ]

    return columns

def getDistanceBetweenLatLngs(latLngArr1, latLngArr2):
    # approximate radius of earth in mi
    R = 3959

    lat1 = radians(latLngArr1[0])
    lon1 = radians(latLngArr1[1])
    lat2 = radians(latLngArr2[0])
    lon2 = radians(latLngArr2[1])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    # distance in MI
    distance = round(R * c, 2)
    return distance

def getTotalDistanceArrOfLatLngs(homeLatLng, arrOfLatLngs):
    startLatLng = homeLatLng # starts at home latLng
    totalDistance = 0
    for latLng in arrOfLatLngs:
        distance = getDistanceBetweenLatLngs(startLatLng, latLng)
        totalDistance += distance
        startLatLng = latLng # change startLatLng to curr one and move on

    return round(totalDistance, 2)

def getDateRangeArr(startDate,endDate):
    '''
    Accepts two dates in YYYY-MM-DD format
    Returns arr of all dates in that range in same fmt
    '''
    dateArr = []

    currDate = startDate
    currDateObj = datetime.strptime(startDate, '%Y-%m-%d')

    # up until the end date included:
    while currDate <= endDate:
        dateArr.append(currDate)
        currDateObj = currDateObj + timedelta(days=1)
        currDate = datetime.strftime(currDateObj, '%Y-%m-%d')

    return dateArr

def getTotalTzChangeArrOfTzs(homeTz, arrOfTzs):
    '''
    Returns absolute TZ change, NOT net
    '''
    startTz = homeTz
    totalTzChange = 0
    for tz in arrOfTzs:
        tzChange = abs(startTz - tz)
        totalTzChange += tzChange
        startTz = tz

    return totalTzChange

def createFinalRowFromDict(rowDict, statType, isTraining):
    '''
    If stat type is 'tpt', exclude nf field
    '''
    fieldsOrder = getColumns()

    finalRow = []

    for field in fieldsOrder:
        # skip adding certain fields based on conditions:
        if (
            (isTraining is not True and field == "actual_stat") 
            or
            (statType == 'tpt' and field == "nf")
        ):
            continue
        
        finalRow.append(rowDict[field])
    
    return finalRow

def createFinalDictFromDict(rowDict, statType, isTraining):
    '''
    If stat type is 'tpt', exclude nf field
    '''
    fieldsToInclude = getColumns()

    finalDict = {}

    for field in fieldsToInclude:
        # skip adding certain fields based on conditions:
        if (
            (isTraining is not True and field == "actual_stat") 
            or
            (statType == 'tpt' and field == "nf")
        ):
            continue
        
        finalDict[field] = rowDict[field]
    
    return finalDict

def getAndPrepFinalData(gameDate, statType, isTraining, numRecentGames, dicts=False):
    baseData = api.getBaseMlData(gameDate, statType, isTraining, numRecentGames)
    gameDateObj = datetime.strptime(gameDate, '%Y-%m-%d')
    oneWeekAgoTimestamp = gameDateObj - timedelta(days=7)
    oneWeekAgoDate = datetime.strftime(oneWeekAgoTimestamp, '%Y-%m-%d')
    preppedData = []

    # calculate extra data for each row & add as properties
    for row in baseData:
        recentGameDates = row["recent_game_dates"]
        # get end index of games from past week
        iOfLastGamePastWeek = next((i for i, v in enumerate(recentGameDates) if v < oneWeekAgoDate), -1)
        
        # num of games past week
        row["num_games_past_week"] = max(iOfLastGamePastWeek, 0)

        # get recent mins stats (account for no data)
        recentMins = row["recent_mins"]
        row["mins_in_past_week"] = round(sum(recentMins[:iOfLastGamePastWeek]), 3)
        if len(recentMins) > 0:
            row["mins_last_game"] = recentMins[0]
            row["avg_mins_last_five"] = mean(recentMins[:5])
            row["avg_mins_last_ten"] = mean(recentMins[:10])
        else:
            row["mins_last_game"] = 0
            row["avg_mins_last_five"] = 0
            row["avg_mins_last_ten"] = 0

        # get avgs of last stats (account for no data)
        recentOfStat = row["recent_of_stat"]
        if len(recentOfStat) > 0:
            row["stat_last_game"] = recentOfStat[0]
            row["avg_stat_last_five"] = mean(recentOfStat[:5])
            row["avg_stat_last_ten"] = mean(recentOfStat[:10])
        else:
            row["stat_last_game"]  = 0
            row["avg_stat_last_five"] = 0
            row["avg_stat_last_ten"] = 0

        # get time since last game
        recentGameTimes = row["recent_game_times"]

        if len(recentGameDates) > 0:
            lastGameDate = datetime.strptime(recentGameDates[0], "%Y-%m-%d")
            lastGameTime = recentGameTimes[0]
        else:
            ## NOTE: will default to end of 2014-2015 season if nothing found
            lastGameDate = datetime.strptime('2015-04-30', "%Y-%m-%d")
            lastGameTime = 1900

        daysSinceInHrs = abs((gameDateObj - lastGameDate).days) * 24
        gameTimeOffset = (row["game_time_24_et"] - lastGameTime) / 100
        row["total_hrs_since_last_game"] = daysSinceInHrs + gameTimeOffset

        # caluclate winning streaks (of games player has played in)
        recentGamesWon = row["recent_games_won"]
        lastFive = recentGamesWon[:5]
        lastTen = recentGamesWon[:10]
        row["win_pct_last_five"] = round(lastFive.count(True) / len(lastFive), 3)
        row["win_pct_last_ten"] = round(lastTen.count(True) / len(lastTen), 3)

        if recentGamesWon[0] is True:
            winningStreak = 1
            losingStreak = 0
            for win in recentGamesWon[1:]:
                if win is True:
                    winningStreak += 1
                else:
                    break
        elif recentGamesWon[0] is False:
            winningStreak = 0
            losingStreak = 1
            for win in recentGamesWon[1:]:
                if win is False:
                    losingStreak += 1
                else:
                    break
        else: # account for no games in arr
            winningStreak = 0
            losingStreak = 0
        
        row["winning_streak"] = winningStreak
        row["losing_streak"] = losingStreak
        
        # calculate distance traveled & time zones
        recentLatLngs = row["recent_latlng"]
        recentTimeZones = row["recent_time_zones"]
        
        # if the player played in the last team game:
        if row["played_in_last_team_game"] == 'true':
            # coors of that game are last
            lastLatLng = recentLatLngs[0]
            lastTz = recentTimeZones[0]
        else:
            # if not, home coors are last
            lastLatLng = row["home_lat_lng"]
            lastTz = row["home_tz_over_utc"]

        row["distance_traveled_for_game"] = getDistanceBetweenLatLngs(row["game_lat_lng"], lastLatLng)
        coordsPastWeek = reversed(recentLatLngs[:iOfLastGamePastWeek])
        # if coords past week is empty arr, total distance will be 0:
        row["distance_traveled_past_week"] = getTotalDistanceArrOfLatLngs(row["home_lat_lng"], coordsPastWeek)

        # calculate time change since last game & total time change in past week
        row["tz_change_for_game"] = row["game_tz"] - lastTz
        tzsPastWeek = reversed(recentTimeZones[:iOfLastGamePastWeek])
        row["tz_change_past_week"] = getTotalTzChangeArrOfTzs(row["home_tz_over_utc"], tzsPastWeek)

        if dicts is True:
            finalDict = createFinalDictFromDict(row, statType, isTraining)
            preppedData.append(finalDict)
        else:
            finalRow = createFinalRowFromDict(row, statType, isTraining)
            preppedData.append(finalRow)
    
    return preppedData

# This fcn primarily used for pulling training data for a date range
def getDataForMultipleDates(dateArr, statType, isTraining, numRecentGames):
    allStats = []

    for date in dateArr:
        dataForDate = getAndPrepFinalData(date, statType, isTraining, numRecentGames)
        allStats.extend(dataForDate)

    return allStats

def pullAzureTrainingDataAndWriteToCsv(dateArr, statType):
    '''
    Pulls in data for multiple dates, in an arr, for a specific stat type
    '''
    folder = './../local-data/'
    filename = 'nba-' + statType + '-azure-initial-training-data.csv'
    location = folder + filename

    print("Pulling factor data from API...")
    data = getDataForMultipleDates(dateArr, statType, True, 10) # training = True

    print("Writing factor data to csv. File location: ", location)
    try:
        csv.writeToCsv(data, location, header=getColumns()) # header row!
        print("CSV WRITE SUCCESS", location)
        return location
    except:
        print("COULDNT WRITE CSV")
        return False

def pullGoogleTrainingDataAndWriteToCsv(dateArr, statType):
    '''
    Pulls in data for multiple dates, in an arr, for a specific stat type
    '''
    folder = './../local-data/'
    filename = 'nba-' + statType + '-google-initial-training-data.csv'
    location = folder + filename

    print("Pulling factor data from API...")
    data = getDataForMultipleDates(dateArr, statType, True, 10) # training = True

    print("Writing factor data to csv. File location: ", location)
    try:
        csv.writeToCsv(data, location) # no header row!
        return location
    except:
        return False


