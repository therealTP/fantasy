from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import requests

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
    # caps = DesiredCapabilities.FIREFOX
    # caps["marionette"] = True

    # browser = webdriver.Firefox()
    browser = webdriver.PhantomJS()
    browser.set_window_size(1124, 850)
    # browser = webdriver.Chrome()

    return browser

def startNoWaitDriver():
    profile = webdriver.FirefoxProfile()
    profile.set_preference("webdriver.load.strategy", "unstable")
    browser = webdriver.Firefox(firefox_profile=profile)

    return browser

def getAllRawHtml():
    rawHtmlDict = {}

    # this is for headless browser scraping
    # display = createVirtualScreen()

    # start fast load driver
    # driver = startNoWaitDriver()

    try:
        # start browser
        driver = startDriver()
        # use for nf & bm projs
        rawHtmlDict["nf"] = nf.getRawHtml(driver)
        rawHtmlDict["bm"] = bm.getRawHtml(driver)

        # start requests session
        session = requests.Session()
        # use for rw & fp projs
        rawHtmlDict["rw"] = rw.getRawHtmlRequests(session)
        rawHtmlDict["fp"] = fp.getRawHtmlRequests(session)

    except Exception as error:
        # TODO: handle this err. Log? Throw?
        print("COULDN'T GET RAW HTML DATA FOR PROJECTIONS, ERROR:", error)

    # clean up
    driver.quit()
    # display.stop() 
    
    return rawHtmlDict

def parseProjsFromHtml(htmlDict):
    # get list of curr players from API
    playerList = api.getCurrentPlayerData()
    gamesToday = api.getTodaysGames()
    parsedProjs = []
    newIds = []

    try:
        # get all projection data from all raw html
        nfData = nf.extractProjections(htmlDict["nf"], playerList, gamesToday)
        rwData = rw.extractProjections(htmlDict["rw"], playerList, gamesToday)
        fpData = fp.extractProjections(htmlDict["fp"], playerList, gamesToday)
        bmData = bm.extractProjections(htmlDict["bm"], playerList, gamesToday)
        # parsedProjs = bmData["projections"]
        # newIds = bmData["newPlayerIds"]
        # concat all projs & missing players into single arrays

        parsedProjs = nfData["projections"] + rwData["projections"] + fpData["projections"] + bmData["projections"]
        newIds = nfData["newPlayerIds"] + rwData["newPlayerIds"] + fpData["newPlayerIds"] + bmData["newPlayerIds"]

        counts = {
            "nf": {
                "projs": len(nfData["projections"]),
                "new_ids": len(nfData["newPlayerIds"]),
                "total_rows": nfData["totalNumRows"]
            },
            "rw": {
                "projs": len(rwData["projections"]),
                "new_ids": len(rwData["newPlayerIds"]),
                "total_rows": rwData["totalNumRows"]
            },
            "fp": {
                "projs": len(fpData["projections"]),
                "new_ids": len(fpData["newPlayerIds"]),
                "total_rows": fpData["totalNumRows"]
            },
            "bm": {
                "projs": len(bmData["projections"]),
                "new_ids": len(bmData["newPlayerIds"]),
                "total_rows": bmData["totalNumRows"]
            },
        }

    except Exception as error:
        # TODO: handle this err. Log? Throw?
        print("COULDN'T PARSE PROJECTIONS, ERROR:", error)

    return {'projections': parsedProjs, 'newPlayerIds': newIds, 'counts': counts}