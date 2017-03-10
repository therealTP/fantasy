import nba.ops.mlDataPrep as ml
import nba.ops.csvOps as csv
import nba.ops.googleApiOps as google
import nba.ops.apiCalls as api
import json
import time

def analyzeModel(statType):
    analyze = google.analyzePredictionModel(stat)

    headers = ml.getColumns()[1:]

    for row in analyze["dataDescription"]["features"]:
        if "numeric" in row:
            print(headers[int(row["index"])], row["numeric"]["mean"], row["numeric"]["variance"])
        elif "categorical" in row:
            print(headers[int(row["index"])], row["categorical"]["count"], row["categorical"]["values"])

def postPredictionsForDates(dateRange, statType):
    # for each date after training phase:
    for date in dateRange:
        # --- DAY OF --- #
        # 1. wait for model to update before getting next predictions (only necessary in simulation)
        # time.sleep(20)

        # 2. get predictions for date & stat type
        predictions = google.getPredictionsForDate(date, statType)
        print("predictions pulled & posting", statType, date)

        # 3. post predicitons to API (given date & brefId of each pred)
        postRes = api.postPredictions('GOOGLE', date, statType, predictions)
        print("Predictions posted for", statType, date)
        
        # -- DAY AFTER -- #
        # 4. retrain model given date & stat type (IRL would happen morning after date)
        retrainRes = google.retrainModelWithDate(date, statType)
        print("Retrain started for ", date)

    return "DONE"

trainRange = ml.getDateRangeArr("2015-11-04", "2015-11-04") # training period, ~ 1/2 season
retrainRange = ml.getDateRangeArr("2015-11-05", "2016-04-18") # last date: 4/18/16
stat = "tov"

# create & train model for stat type:
# createResponse = google.createAndTrainNewModelWithDateRange(trainRange, stat)
# google.waitForModelToRetrain(stat)

# pull predictions for date range & stat type, retain each iteration
postPredictionsForDates(retrainRange, stat)

# delete model when finished
# google.deletePredictionModel(stat)

# google.listPredictionModels()
# print(google.getTrainingStatusOfModel(stat))




