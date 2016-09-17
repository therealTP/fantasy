import boto3
import json
import csv

def connectToS3Bucket():
    return boto3.resource('s3')

def putObjectS3(data_object, bucket, bucket_location=""):
    """
    data object is file of json to put
    bucket_location is optional folder name in bucket
    """
    try:
        # create s3 object
        s3 = boto3.resource('s3')

        # open data object to post
        data = open(data_object, 'rb')

        # create object key based on bucket location & data object name
        object_key = bucket_location + data_object

        # put object into bucket
        s3.Bucket(bucket).put_object(Key=object_key, Body=data)

        # return true for success
        return True

    except:
        # return false for failure
        return False

def getObjectS3(bucket, key):
    """
    get s3 json object
    return python dict
    """
    try:
        # create s3 object
        s3 = boto3.resource('s3')

        # get object, decode, convert to python dict
        dataObj = json.loads(s3.Object(bucket, key).get()['Body'].read().decode('utf-8'))

        return dataObj

    except:
        # return false for failure
        return False

def getManyObjectsS3(bucket, keyArr):
    """
    Take in bucket name & arr of keys
    Return dict with all bucket vals
    """

    try:
        # create s3 object
        s3 = boto3.resource('s3')
        
        # dict to store all data
        bucketData = {}

        for key in keyArr:
            # try to pull data for key
            try:
                data = json.loads(s3.Object(bucket, key).get()['Body'].read().decode('utf-8'))
                bucketData[key] = data
            # if error go to next key
            except:
                continue
        
        return bucketData
    except:
        return False

def getObjectsFromBucket(bucket, prefix):
    try:
        # create s3 object
        s3 = boto3.client('s3')

        return s3.list_objects(Bucket=bucket, Prefix=prefix)["Contents"]
    except Exception as e:
        print("ERROR", e)

def getKeysFromObjArr(objArr):
    keys = []

    for obj in objArr:
        keys.append(obj["Key"])
    
    return keys

def writeProjsToFile(projData):
    with open('projections.json', 'w') as outfile:
        json.dump(projData, outfile)

def openProjFile(projFile):
    with open(projFile) as infile:    
        data = json.load(infile)
    return data

def parseRawProjData(rawData):

    parsedData = []
    totalCount = 0

    for day, data in rawData.items():

        cleanDate = day.replace("daily-projections/", "").replace(".json", "")
        print("getting projs from ", cleanDate)

        for src, srcData in data.items():

            if src == "game_date":
                continue
            elif src == "number_fire":
                srcId = 1
            elif src == "basketball_monster":
                srcId = 2
            elif src == "roto_wire":
                srcId = 3
            elif src == "fantasy_pros":
                srcId = 4

            try: 
                scrape_timestamp = srcData["scrape_timestamp_pst"]
            except:
                scrape_timestamp = None

            try:
                projections = srcData["projections"].items()
                srcCount = 0
                
                for playerId, proj in projections:
                    if playerId in ("1144"):
                        # continue    
                        row = []
                        row.extend((playerId, srcId, cleanDate, scrape_timestamp, proj["min"], proj["pts"], proj["reb"],
                                    proj["ast"], proj["stl"], proj["blk"], proj["tov"], proj["3pt"]))
                        parsedData.append(row)
                        srcCount += 1
                        totalCount += 1
                
                print(srcCount, " from src id ", srcId)

            except:
                continue

    print(totalCount, " total projs parsed")
    return parsedData

def writeFinalProjsToCsv(finalProjArr):
    fileName = 'extra-projection-data.csv'
    with open(fileName, 'w') as f:
        wtr = csv.writer(f, delimiter= ',')
        wtr.writerows(finalProjArr)

# bucket = 'nba-data-2015-2016'
# objs = getObjectsFromBucket(bucket, 'daily-projections/2')
# keyArr = getKeysFromObjArr(objs)
# rawData = getManyObjectsS3(bucket, keyArr)
# writeProjsToFile(rawData)

projFile = 'projections.json'

rawData = openProjFile(projFile)
parsedData = parseRawProjData(rawData)
writeFinalProjsToCsv(parsedData)

# print(parsedData)

                

