from pyvirtualdisplay import Display
from selenium import webdriver

import nba.scrapers.number_fire_scraper as nf
import nba.scrapers.rotowire_scraper as rw
import nba.scrapers.fantasy_pros_scraper as fp
import nba.scrapers.bball_monster_scraper as bm

import nba.ops.apiCalls as api 

def createVirtualScreen():
    # open a virtual display to run on python anywhere
    display = Display(visible=0, size=(800, 600))
    display.start()

    return display

def startDriver():
    return webdriver.Firefox()

def getPlayerList():
    return api.getCurrentPlayerData()

def getAllRawHtml():
    rawHtmlDict = {}

    # this is for headless browser scraping
    display = createVirtualScreen()

    # start browser
    driver = startDriver()

    try:
        # rawHtmlDict["nf"] = nf.getRawHtml(driver)
        # rawHtmlDict["rw"] = rw.getRawHtml(driver)
        # rawHtmlDict["fp"] = fp.getRawHtml(driver)
        rawHtmlDict["bm"] = bm.getRawHtml(driver)
    except Exception as error:
        # TODO: handle this err. Log? Throw?
        print("COULDN'T GET RAW HTML DATA FOR PROJECTIONS, ERROR:", error)

    # clean up
    driver.quit()
    display.stop() 

    return rawHtmlDict

def parseProjsFromHtml(htmlDict):
    parsedProjs = []
    missingPlayers = []

    # get list of curr players from API
    playerList = getPlayerList()

    try:
        # nfData = nf.extractProjections(htmlDict["nf"], playerList)
        # rwData = rw.extractProjections(htmlDict["rw"], playerList)
        # fpData = fp.extractProjections(htmlDict["fp"], playerList)
        bmData = bm.extractProjections(htmlDict["bm"], playerList)
        parsedProjs.extend(bmData["projections"])
        missingPlayers.extend(bmData["missingPlayers"])
    except Exception as error:
        # TODO: handle this err. Log? Throw?
        print("COULDN'T GET RAW HTML DATA FOR PROJECTIONS, ERROR:", error)

    return {'projections': parsedProjs, 'missingPlayers': missingPlayers}

rawProjHtml = getAllRawHtml()
projectionDict = parseProjsFromHtml(rawProjHtml)
print(projectionDict)



