import nba.ops.mlDataPrep as ml
import nba.ops.csvOps as csv
import nba.ops.googleApiOps as google
import nba.ops.azureMlOps as az

import time

def trainGoogleModelFromCsv(filename, location, stat):
    '''
    Location: location of file locally
    Filename: waht you want the file to be called in google storage
    '''
    print("Uploading csv to google storage")

    # upload csv to google storage
    storageLoc = google.uploadCsvToGoogleStorage(filename, location)
    print("STORED AT", storageLoc)

    print("Creating and training prediction model")
    # create & train model w/ uploaded data
    response = google.createAndTrainNewModel(stat, storageLoc)

    trainingFinished = False
    WAIT_TIME = 5

    while trainingFinished is False:
        print("Model still training...")
        status = google.getTrainingStatusOfModel(stat)
        if status['trainingStatus'] == 'DONE':
            trainingFinished = True
        elif status['trainingStatus'] == 'RUNNING':
            time.sleep(WAIT_TIME)
            continue

    print("Training finished. Getting model info.")
    print(google.getTrainingStatusOfModel(stat))

def predictDataForDates(dateArr, statType, isTraining, numRecentGames):
    # get data
    data = ml.getDataForMultipleDates(dateArr, statType, isTraining, numRecentGames)

    for row in data:
        # exclude actual val from training
        predictTest = row[1:]
        prediction = google.getPrediction(stat, predictTest)
        print("ACTUAL", row[0], "PRED", prediction)

    return "DONE"

def createDictFromRow(row, columnsArr):
    newDict = {}

    for index, column in enumerate(columnsArr):
        newDict[column] = row[index]

    return newDict

trainDates = ml.getDateRangeArr('2015-11-04', '2015-11-05')
stat = 'reb'
isTraining = True
numRecentGames = 10

filename = 'nba-pts-google-initial-training-data.csv'
location = './../local-data/nba-pts-google-initial-training-data.csv'

# ml.pullGoogleTrainingDataAndWriteToCsv(trainDates, stat)
# time.sleep(5)
# trainGoogleModelFromCsv(filename, location, stat)

# google.deletePredictionModel(stat)

# predictDate = ['2016-01-05']

# pullTrainingDataAndTrainModel(trainDates, stat, isTraining, numRecentGames)
# predictDataForDates(predictDate, stat, isTraining, numRecentGames)

# google.retrainModelWithDate('2015-11-07', stat)
# google.waitForModelToRetrain(stat)

# counttest = 0
# num = 0
analyzeData = google.analyzePredictionModel(stat)
print(analyzeData)
# for value in analyzeData["dataDescription"]["features"][4]["categorical"]["values"]:
#     counttest += int(value["count"])
#     num += 1

# print("COUNT", counttest, "NUM", num)




