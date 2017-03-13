from selenium import webdriver
from selenium.webdriver.support.ui import Select
from lxml import html
import datetime
import csv
import json

def fillOutAndSubmitForm(teamName, month):
    # go to form url
    form_url = 'http://www.oddsshark.com/nba/database'
    browser.get(form_url)

    # get relevant fields
    teamNameInput = browser.find_element_by_id('team-search-h2h')
    monthSelect = Select(browser.find_element_by_id('chalk-select-month-h2h'))
    gameTypeSelect = Select(browser.find_element_by_id('chalk-select-game-type-h2h'))
    locationAnyRadio = browser.find_element_by_id('location-any-h2h')
    games20Radio = browser.find_element_by_id('games-20-h2h')
    favoriteSelect = Select(browser.find_element_by_id('chalk-select-odds-h2h'))

    teamNameInput.clear()
    teamNameInput.send_keys(teamName)
    monthSelect.select_by_visible_text(month)
    games20Radio.click()
    gameTypeSelect.select_by_visible_text('Regular Season')
    locationAnyRadio.click()
    favoriteSelect.select_by_visible_text('Either')

    # submit form, will take to next page:
    submitButton = browser.find_element_by_id('submit-h2h')
    submitButton.click()

def getDataFromResultsPage():
    # get data from results page
    tree = html.fromstring(browser.page_source)

    resultRows = tree.cssselect('div#block-system-main table.base-table:last-child tbody tr')

    return resultRows

def scrapeLineData(teams):
    allLineData = []
    # months = ['October']
    months = ["October", "November", "December", "January", "February", "March", "April"]

    for team in teams:
        for month in months:
            print("Scraping ", month, " data for ", team)
            fillOutAndSubmitForm(team, month)
            results = getDataFromResultsPage()
            print(len(results), " scraped")
            allLineData.extend(results)
            # browser.execute_script("window.history.go(-1)")

    return allLineData

def parseLineData(lineData):
    parsedLineData = []
    
    for tr in lineData:
        lineArr = []

        rawGameDate =       tr[0].text_content()
        gameDate =          datetime.datetime.strptime(rawGameDate, '%b %d, %Y').strftime('%Y-%m-%d')
        awayTeam =          tr[1].text_content()
        awayTeamScore =     tr[2].text_content()
        # awayTeamScore =     int(tr[2].text_content())
        homeTeam =          tr[3].text_content()
        homeTeamScore =     tr[4].text_content()
        homeSpread =        tr[6].text_content()
        # homeSpread =        float(tr[6].text_content())
        total =             tr[8].text_content()
        # total =             float(tr[8].text_content())
        overOrUnder =       tr[9].text_content()

        lineArr.extend((gameDate, awayTeam, awayTeamScore, homeTeam, homeTeamScore, homeSpread, total, overOrUnder))
        parsedLineData.append(lineArr)

    return parsedLineData

# start browser
# browser = webdriver.Firefox()

teamsToScrape = ["Atlanta", "Boston", "Brooklyn", "Charlotte", "Chicago", "Cleveland", 
"Dallas", "Denver", "Detroit", "Golden State", "Houston", "Indiana", "LA Clippers", "LA Lakers",
"Memphis", "Miami", "Milwaukee", "Minnesota", "New Orleans", "New York", "Oklahoma City", "Orlando", 
"Philadelphia", "Phoenix", "Portland", "Sacramento", "San Antonio", "Toronto", "Utah", "Washington"]

# rawLineData = scrapeLineData(teamsToScrape)
# parsedData = parseLineData(rawLineData)
# print("TOTAL SCRAPED:", len(parsedData))

# with open("./../scraped-data/game-line-data.csv", "w") as f:
#     writer = csv.writer(f)
#     writer.writerows(parsedData)

# browser.quit()

def getTeamAbbrevDict():
    with open('./../json-data/team-abbrev-to-id.json') as data_file:
        teamAbbrevDict = json.load(data_file)

    return teamAbbrevDict

def finalizeLineData(lineData, teamAbbDict):
    finalLineData = []
    cutoff = datetime.date(2015, 10, 1)
    for line in lineData:
        lineArr = []

        gameDate =          line[0]

        # check if from prev seasons:
        if datetime.datetime.strptime(gameDate, '%Y-%m-%d').date() < cutoff:
            continue

        awayTeam =          line[1]
        awayTeamScore =     line[2]
        homeTeam =          line[3]
        homeTeamScore =     line[4]
        homeSpread =        float(line[5])
        total =             float(line[6])
        overOrUnder =       line[7]
        awayTeamProjPts =   0.5 * total + (0.5 * homeSpread)
        homeTeamProjPts =   0.5 * total - (0.5 * homeSpread)


        #check if game already present in final data:
        if len([x for x in finalLineData if x[0] == gameDate and x[1] == awayTeam and x[3] == homeTeam]):
            continue
        else:
            lineArr.extend((gameDate, awayTeam, homeTeam, homeSpread, total, overOrUnder, awayTeamProjPts, homeTeamProjPts))
            finalLineData.append(lineArr)

    print("TOTAL CLEANED", len(finalLineData))
    return finalLineData

with open("./../scraped-data/game-line-data.csv", "r") as f:
    reader = csv.reader(f)
    lines = list(reader)

teamAbbrevs = getTeamAbbrevDict()

finalData = finalizeLineData(lines, teamAbbrevs)

with open("./../scraped-data/game-line-data.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerows(finalData)


