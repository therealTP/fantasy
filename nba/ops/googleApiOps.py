# AUTH TO GCLOUD THROUGH SDK: https://googlecloudplatform.github.io/google-cloud-python/stable/google-cloud-auth.html
# BETA Python3 Google App Engine: https://cloudplatform.googleblog.com/2016/08/python-3-on-Google-App-Engine-flexible-environment-now-in-beta.html
# Manage SDK Components via CLI
# Supported cloud services: https://developers.google.com/api-client-library/python/apis/?authuser=1
# Prediction dev guide: https://cloud.google.com/prediction/docs/developer-guide
# Prediction API Python Ref: https://developers.google.com/resources/api-libraries/documentation/prediction/v1.6/python/latest/prediction_v1.6.trainedmodels.html#get
import logging
import os
import sys
import json
import pprint
import nba.ops.mlDataPrep as ml
import time
import csv

from gcloud import storage
from apiclient.discovery import build
import nba.ops.csvOps as csvOps
import nba.ops.jsonData as jsonData
from nba.ops.config import APP_CONFIG

config = APP_CONFIG["GOOGLE_CLOUD"]

def uploadCsvToGoogleStorage(filename, location):
    client = storage.Client(config["PROJECT_ID"])
    bucket = client.get_bucket(config["STORAGE_BUCKET"])
    blob = bucket.blob(filename)

    with open(location, 'rb') as csv_file:
        blob.upload_from_file(csv_file)

    # return location of file: bucket + filename
    return config["STORAGE_BUCKET"] + "/" + filename

def getCsvFromCloudStorageToFile(bucket, filename):
    client = storage.Client(config["PROJECT_ID"])
    bucket = client.get_bucket(bucket)
    blob = bucket.get_blob(filename)

    local_file = jsonData.LOCAL_DATA_PATH + filename

    with open(local_file, 'wb') as file_obj:
        blob.download_to_file(file_obj)

    return local_file # return localfilename

def createAndTrainNewModel(statType, trainDataLocation):
    '''
    Can also be used to re-insert model to retrain
    '''
    service = build('prediction', 'v1.6')
    trainer = service.trainedmodels()

    modelId = config["MODEL_IDS"][statType]
    modelType = 'REGRESSION'

    trainBody = {
        "id": modelId,
        "storageDataLocation": trainDataLocation,
        "modelType": modelType 
    }

    return trainer.insert(project=config["PROJECT_ID"], body=trainBody).execute()

def createAndTrainNewModelWithDateRange(dateRange, statType):
    trainingDataLoc = ml.pullGoogleTrainingDataAndWriteToCsv(dateRange, statType)
    filename = config["TRAINING_DATA_FILES"][statType]
    uploadLocation = uploadCsvToGoogleStorage(filename, trainingDataLoc)
    createModelResponse = createAndTrainNewModel(statType, uploadLocation)
    
    # cleanup
    os.remove(trainingDataLoc)
    return createModelResponse

def listPredictionModels():
    service = build('prediction', 'v1.6')
    trainer = service.trainedmodels()

    return trainer.list(project=config["PROJECT_ID"]).execute()

def analyzePredictionModel(statType):
    service = build('prediction', 'v1.6')
    trainer = service.trainedmodels()
    modelId = config["MODEL_IDS"][statType]
    return trainer.analyze(project=config["PROJECT_ID"], id=modelId).execute()

def getTrainingStatusOfModel(statType):
    service = build('prediction', 'v1.6')
    trainer = service.trainedmodels()
    modelId = config["MODEL_IDS"][statType]
    return trainer.get(project=config["PROJECT_ID"], id=modelId).execute()

def getPrediction(statType, featureArr):
    service = build('prediction', 'v1.6')
    predictor = service.trainedmodels()

    modelId = config["MODEL_IDS"][statType]

    body = {
        'input': {
            'csvInstance': featureArr
        }
    }

    try:
        predictionResponse = predictor.predict(project=config["PROJECT_ID"], id=modelId, body=body).execute()
        return max(float(predictionResponse["outputValue"]), float(0)) # prevent negative vals
    except Exception as e:
        if e.__class__.__name__ == 'googleapiclient.errors.HttpError':
            print("CAUGHT HTTP ERR GOOGLE")
            time.sleep(105)
            predictionResponse = predictor.predict(project=config["PROJECT_ID"], id=modelId, body=body).execute()
            return max(float(predictionResponse["outputValue"]), float(0)) # prevent negative vals
        else:
            raise ValueError("Error getting prediction")

def getPredictionsForDate(date, statType):
    predictData = ml.getAndPrepFinalData(date, statType, False, 10)

    predictionsForDate = []

    print(" -- Now Pulling predictions for", date)

    for row in predictData:
        rowObj = {}

        # get bref id for row
        if statType == 'tpt':
            rowObj["bref_id"] = row[3]
        else:
            rowObj["bref_id"] = row[4]

        rowObj["Scored Label"] = getPrediction(statType, row)

        predictionsForDate.append(rowObj)
    
    return predictionsForDate

def deletePredictionModel(statType):
    service = build('prediction', 'v1.6')
    deleter = service.trainedmodels()

    modelId = config["MODEL_IDS"][statType]
    
    return deleter.delete(project=config["PROJECT_ID"], id=modelId).execute()

def retrainModel(statType, retrainRows):
    service = build('prediction', 'v1.6')
    retrainer = service.trainedmodels()
    modelId = config["MODEL_IDS"][statType]

    for row in retrainRows:
        body = {
            "output": int(row[0]), # The generic output value - could be regression value or class label
            "csvInstance": row[1:]
        }

        retrainer.update(project=config["PROJECT_ID"], id=modelId, body=body).execute()

    return "RETRAIN FINISHED"

def retrainModelWithNewCsv(statType, retrainRows):
    # if no new rows, return:
    if len(retrainRows) == 0:
        print("NO NEW ROWS TO ADD")
        return

    service = build('prediction', 'v1.6')

    # get initial training data for model + save to local csv
    local_file = getCsvFromCloudStorageToFile(config["STORAGE_BUCKET"], config["TRAINING_DATA_FILES"][statType])

    # append retrain rows to local csv
    csvOps.appendToCsv(retrainRows, local_file)
    
    # reupload new csv to cloud, overwrite old file
    upload_location = uploadCsvToGoogleStorage(config["TRAINING_DATA_FILES"][statType], local_file)

    # re-insert model, which will re-train with new data, even though filename is the same
    createAndTrainNewModel(statType, upload_location)

    # cleanup: delete local version of file
    os.remove(local_file)

    return "NEW MODEL PUBLISHED"

def retrainModelWithDate(gameDate, statType):
    retrainRows = ml.getAndPrepFinalData(gameDate, statType, True, 10)
    # return retrainModel(statType, retrainRows)
    return retrainModelWithNewCsv(statType, retrainRows)

def waitForModelToRetrain(statType):
    startTime = time.time()
    print("Waiting for model to retrain...")
    while True:
        trainingStatusRes = getTrainingStatusOfModel(statType)
        status = trainingStatusRes["trainingStatus"]

        if status == 'DONE':
            endTime = time.time()
            timeToRun = endTime - startTime
            print("Retrain complete. Seconds to retrain: " + str(round(timeToRun, 1)))
            # sys.stdout.flush()
            return 'DONE'
        else:
            # sys.stdout.write("\rModel still training with status " + status)
            # sys.stdut.flush()
            time.sleep(5)
            continue

def retrainAllModelsWithYesterdaysDataAndLog():
    DATE_FORMAT = '%Y-%m-%d'
    yesterday_utc = datetime.now(tz=pytz.utc) - timedelta(days=1)
    yesterday_pst = yesterday_utc.astimezone(timezone('US/Pacific')).strftime(DATE_FORMAT)

    stats = ['pts', 'reb', 'ast', 'stl', 'blk', 'tov', 'tpt']
    retrainModelWithDate(yesterday_pst, stat)
    waitForModelToRetrain(stat)
    analyzeData = analyzePredictionModel(statType)
    logger.logRetrainGoogleModelSuccess(stat, analyzeData["dataDescription"]["outputFeature"]["numeric"]["count"])



    



