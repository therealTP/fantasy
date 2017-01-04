import requests
import json
import csv
import re
from lxml import html
import datetime

def getBrefIdToPlayerIdDict():
    # import player id as dict
    with open('./../local-data/bref-id-to-player-id.json') as data_file:
        playerIdDict = json.load(data_file)

    return playerIdDict

BASE_URL = 'http://www.basketball-reference.com/players/'
URL_EXT = '.html'

def getPlayerInfo(brefId, sessionObj):
    firstLetter = brefId[0]
    playerUrl = BASE_URL + firstLetter + "/" + brefId + URL_EXT
    page = sessionObj.get(playerUrl)
    tree = html.fromstring(page.text)
    # try to get pos w/ no nickname row, i.e. 2nd p elem
    metaPs = tree.cssselect("#meta p")
    for p in metaPs:
        try:
            if p.cssselect('strong')[0].text_content().strip() == 'Position:':
                rawPlayerPosition = p.xpath("child::node()")[2].split("and")[0]
                break
        except:
            pass

    # get pos based on capital letters in text node
    playerPosition = re.sub('[^A-Z]', '', rawPlayerPosition)

    # account for weird positions, e.g. 'Forward/Center'
    if playerPosition == 'FC':
        playerPosition = 'PF'
    elif playerPosition == 'GF':
        playerPosition = 'SG'

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

    # get contract data, either from contract div or salary div:
    try:
        contractCommentStr = str(tree.cssselect('#all_all_contracts')[0].getchildren()[2]).replace("<!--", "").replace("-->", "").replace("</tbody>", "")
        contractTree = html.fromstring(contractCommentStr)
        salary = int(contractTree.cssselect('table tr td span')[0].text_content().replace(',','').replace('$',''))
    except IndexError:
        salaryCommentStr = str(tree.cssselect('#all_all_salaries')[0].getchildren()[2]).replace("<!--", "").replace("-->", "")
        salaryTree = html.fromstring(salaryCommentStr)
        salary = int(salaryTree.cssselect('table tbody tr')[-1].cssselect('td')[-1].text_content().replace(',','').replace('$',''))
    except Exception as e:
        salary = None

    playerInfo = {
        'brefId': brefId,
        'playerPosition': playerPosition,
        'height': height,
        'weight': weight,
        'birthdate': birthdate,
        'debutDate': debutDate,
        'drafted': drafted,
        'gamesPlayed': gamesPlayed,
        'salary': salary
    }

    return playerInfo

def getInfoForAllPlayers(playerIdDict, sessionObj):
    allPlayerData = []
    for brefId in playerIdDict:
        print("getting info for ", brefId)
        playerInfo = getPlayerInfo(brefId, sessionObj)
        allPlayerData.append(playerInfo)

    return allPlayerData

def getRwInfoForPlayer(rwId, sessionObj):
    RW_URL = 'http://www.rotowire.com/basketball/player.htm?id='
    rwPlayerUrl = RW_URL + str(rwId)
    page = sessionObj.get(rwPlayerUrl)
    tree = html.fromstring(page.text)

    name = tree.cssselect('.mlb-player-nameteam h1')[0].text_content().strip().replace("'", "")
    return name

def getBrefIdFromName(playerName, sessionObj):
    PLAYER_LIST_URL = 'http://www.basketball-reference.com/players/'
    firstLetterOfLastName = playerName.strip().split(" ")[-1][0].lower()
    urlToSearch = PLAYER_LIST_URL + firstLetterOfLastName + '/'
    page = sessionObj.get(urlToSearch)
    tree = html.fromstring(page.text)

    playerThs = tree.cssselect('[data-stat="player"]')
    # print(playerThs)

    for playerTh in playerThs:
        playerBrefId = playerTh.get("data-append-csv")
        
        #skip if bref id is none/ first row
        if playerBrefId is None:
            continue

        # if player has a strong element, i.e. he is active:
        if(len(playerTh.cssselect('strong')) == 1):
            # check if that active player matches the name
            playerNameToCheck = playerTh.text_content()
            if playerNameToCheck.lower() == playerName.lower():
                return playerBrefId

    # no exact match? return none
    return None