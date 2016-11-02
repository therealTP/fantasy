import requests
import json
import csv
from lxml import html
import datetime

def getBrefIdToPlayerIdDict():
    # import player id as dict
    with open('./../local-data/bref-id-to-player-id.json') as data_file:
        playerIdDict = json.load(data_file)

    return playerIdDict

def getPlayerInfo(brefId, sessionObj):
    firstLetter = brefId[0]
    playerUrl = BASE_URL + firstLetter + "/" + brefId + URL_EXT
    page = sessionObj.get(playerUrl)
    tree = html.fromstring(page.text)

    height_arr = tree.cssselect('[itemprop="height"]')[0].text_content().split("-")
    height = int(height_arr[0]) * 12 + int(height_arr[1])

    weight = int(tree.cssselect('[itemprop="weight"]')[0].text_content().replace('lb',''))
    birthdate = tree.cssselect('#necro-birth')[0].get('data-birth')

    try:
        gamesPlayed = int(tree.cssselect('div.stats_pullout div.p1 div p')[0].text_content())
    except IndexError:
        gamesPlayed = 0
    # minsPlayed = int(tree.cssselect('table#totals tfoot tr')[0].text_content())
    
    meta_arr = tree.cssselect('div#meta div:last-child p')
    for elem in meta_arr:
        try:
            labelText = elem.cssselect('strong')[0].text_content()
            # print(labelText)
            if 'Draft' in labelText:
                draftArr = elem.xpath("child::node()") # gets all node children of elem
            elif 'NBA Debut' in labelText:
                rawDebutDate = elem.cssselect('a')[0].text_content()
        except IndexError:
            continue
    
    try:
        drafted = int(draftArr[4].split(' ')[5][:-2])
    except UnboundLocalError:
        drafted = 61 # 61 is undrafted, higher draft pos that any drafted player

    try:
        debutDate = datetime.datetime.strptime(rawDebutDate, '%B %d, %Y').strftime('%Y-%m-%d')
    except UnboundLocalError:
        debutDate = '2016-10-26'

    salarytree = html.fromstring(str(tree.cssselect('#all_all_salaries')[0].getchildren()[2]).replace("<!--", "").replace("-->", ""))
    salary = int(salarytree.cssselect('table tbody tr')[-1].cssselect('td')[-1].text_content().replace(',','').replace('$',''))
    playerArr = [brefId, height, weight, birthdate, debutDate, drafted, gamesPlayed, salary]
    print(playerArr)

    return playerArr

def getInfoForAllPlayers(playerIdDict, sessionObj):
    allPlayerData = []
    for brefId in playerIdDict:
        print("getting info for ", brefId)
        playerInfo = getPlayerInfo(brefId, sessionObj)
        allPlayerData.append(playerInfo)

    return allPlayerData
    

BASE_URL = 'http://www.basketball-reference.com/players/'
URL_EXT = '.html'

# start session
session = requests.Session()

# get player dict
playerDict = getBrefIdToPlayerIdDict()

# getPlayerInfo('cottobr01', session)
playerData = getInfoForAllPlayers(playerDict, session)

with open("./../scraped-data/player-update-data.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerows(playerData)