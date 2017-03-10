import nba.ops.mlDataPrep as ml
import nba.ops.azureMlOps as az
import nba.ops.apiCalls as api

# get dates after training phase
dates = ml.getDateRangeArr("2016-01-26", "2016-04-06")
testDate = "2016-01-05"
statType = 'tov'

def getPredsAndRetrainDateRange(dateRange, statType):
    # for each date after training phase:
    for date in dateRange:
        # --- DAY OF --- #
        # 1. get predictions for date & stat type
        predictions = az.getPredictionsForDate(date, statType)
        print("predictions pulled & posting", date)
        # break

        # 2. post predicitons to API (given date & brefId of each pred)
        postRes = api.postPredictions('AZURE', date, statType, predictions)
        # print("POST RES", postRes.json())
        
        # -- DAY AFTER -- #
        # 3. retrain model given date & stat type (IRL would happen morning after date)
        # retrainRes = az.retrainModelWithDate(date, statType)

# print(ml.getAndPrepFinalData('2016-01-05', 'pts', False, 10, True)[0])

# preds = az.getPredictionsForDate(testDate, statType)

# post = api.postPredictions("AZURE", testDate, statType, preds)

getPredsAndRetrainDateRange(dates, statType)




