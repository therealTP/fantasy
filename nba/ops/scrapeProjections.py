from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

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
    caps = DesiredCapabilities.FIREFOX
    caps["marionette"] = True

    browser = webdriver.Firefox(capabilities=caps)
    return webdriver.Firefox()

def getAllRawHtml():
    rawHtmlDict = {}

    # this is for headless browser scraping
    display = createVirtualScreen()

    # start browser
    driver = startDriver()

    try:
        # rawHtmlDict["nf"] = nf.getRawHtml(driver)
        rawHtmlDict["rw"] = rw.getRawHtml(driver)
        rawHtmlDict["fp"] = fp.getRawHtml(driver)
        rawHtmlDict["bm"] = bm.getRawHtml(driver)
    except Exception as error:
        # TODO: handle this err. Log? Throw?
        print("COULDN'T GET RAW HTML DATA FOR PROJECTIONS, ERROR:", error)

    # clean up
    driver.quit()
    display.stop() 

    return rawHtmlDict

def parseProjsFromHtml(htmlDict):
    # get list of curr players from API
    playerList = api.getCurrentPlayerData()
    gamesToday = api.getTodaysGames()
    parsedProjs = []
    newIds = []

    try:
        # get all projection data from all raw html
        # nfData = nf.extractProjections(htmlDict["nf"], playerList, gamesToday)
        rwData = rw.extractProjections(htmlDict["rw"], playerList, gamesToday)
        fpData = fp.extractProjections(htmlDict["fp"], playerList, gamesToday)
        bmData = bm.extractProjections(htmlDict["bm"], playerList, gamesToday)

        # concat all projs & missing players into single arrays
        # parsedProjs = nfData["projections"] + rwData["projections"] + fpData["projections"] + bmData["projections"]
        # newIds = nfData["newPlayerIds"] + rwData["newPlayerIds"] + fpData["newPlayerIds"] + bmData["newPlayerIds"]
        parsedProjs = rwData["projections"] + fpData["projections"] + bmData["projections"]
        newIds = rwData["newPlayerIds"] + fpData["newPlayerIds"] + bmData["newPlayerIds"]
        # parsedProjs = bmData["projections"]
        # newIds = bmData["newPlayerIds"]

    except Exception as error:
        # TODO: handle this err. Log? Throw?
        print("COULDN'T GET RAW HTML DATA FOR PROJECTIONS, ERROR:", error)

    return {'projections': parsedProjs, 'newPlayerIds': newIds}



