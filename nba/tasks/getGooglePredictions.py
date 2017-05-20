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

def getAndPostPredictionsForDates(dateRange, statType):
    # for each date after training phase:
    for date in dateRange:
        # --- DAY OF --- #
        # 1. get predictions for date & stat type
        predictions = google.getPredictionsForDate(date, statType)
        print("predictions pulled & posting", statType, date)

        # 2. post predicitons to API (given date & brefId of each pred)
        postRes = api.postPredictions('GOOGLE', date, statType, predictions)
        
        if postRes != None:
            print("Predictions posted for", statType, date, ". Now pulling retraining data...")
        
        # -- DAY AFTER -- #
        # 3. retrain model given date & stat type (IRL would happen morning after date)
        retrainRes = google.retrainModelWithDate(date, statType)
        print("Retrain started for ", date)

        # 4. wait for model to retrain, then analyze
        google.waitForModelToRetrain(statType)
        analyzeData = google.analyzePredictionModel(statType)
        print("# OUTPUT ROWS:", analyzeData["dataDescription"]["outputFeature"]["numeric"]["count"])

    return "DONE"

def get_predictions_for_stat(stat, startDate, endDate, training=True):
    trainRange = ml.getDateRangeArr("2015-11-04", "2015-11-06") # initial training: first three days when all data is available
    retrainRange = ml.getDateRangeArr(startDate, endDate) # last date: 4/18/16

    # create & train model for stat type:
    if training is True:
        createResponse = google.createAndTrainNewModelWithDateRange(trainRange, stat)
        google.waitForModelToRetrain(stat)

    # pull predictions for date range & stat type, retain each iteration
    getAndPostPredictionsForDates(retrainRange, stat)

    return "DONE!"


# -- MODEL OPS -- #
# google.deletePredictionModel(stat)
# print(google.listPredictionModels())
print(json.dumps(google.analyzePredictionModel("pts")))




