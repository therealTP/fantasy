import json
from sys import path
path.append('./../../../config/')
import fantasyconf as env
import psycopg2 as db

# pull in player data
def getRawPlayerData():
    with open('./../json-data/player_data.json') as data_file:    
        data = json.load(data_file)
    
    return data

# parse/ prep player data
def prepPlayerData(rawPlayerData):
    playerDataArr = []
    for id, playerData in rawPlayerData.items():
        playerDataArr.append((
            id, 
            playerData["name"], 
            playerData.get("pos"),
            playerData.get("nf_id"),
            playerData.get("fp_id"),
            playerData.get("bref_id"),
            playerData.get("bm_id"),
            playerData.get("fc_id"),
            playerData.get("rw_id")                                                        
            ))

    return playerDataArr

# Connect to an existing database
def connectToDb():
    conn = db.connect(
        host=env.DB_HOST, 
        port=env.DB_PORT, 
        database=env.DB_NAME, 
        user=env.DB_USER, 
        password=env.DB_PW
        )

    return conn

# insert player data into db
def insertPlayerDataIntoDb(dataArr, dbConn):
    query = "INSERT INTO nba_players \
            (player_id, player_name, player_position, nf_id, fp_id, bref_id, bm_id, fc_id, rw_id) \
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    dbConn.cursor().executemany(query, dataArr)
    dbConn.commit()

rawPlayerData = getRawPlayerData()
preppedData = prepPlayerData(rawPlayerData)
conn = connectToDb()
insertPlayerDataIntoDb(preppedData, conn)