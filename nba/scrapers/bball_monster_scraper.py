from pyvirtualdisplay import Display
from selenium import webdriver
from lxml import html
import DataSuite as ds
import PlayerSuite as ps
import linksFilesCreds as lfc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json


def checkForElement(browsObj, elemName):
    """
    """
    elem = WebDriverWait(browsObj, 10).until(
        EC.presence_of_element_located((By.NAME, elemName)))

    return elem

def getHtmlTreeFromPage(login_url, user, pw, page_url):
    """
    """
    # open a virtual display to run on python anywhere
    display = Display(visible=0, size=(800, 600))
    display.start()

    # create selenium browser
    browser = webdriver.Firefox()
    browser.get(login_url)

    # get user/pass elements
    username = browser.find_element_by_name(lfc.BM_LOGIN_FIELD)
    password = browser.find_element_by_name(lfc.BM_PW_FIELD)

    # fill in user/pass fields
    username.send_keys(user)
    password.send_keys(pw)

    # print (browser.current_url)

    # click login button
    login_button = browser.find_element_by_id(lfc.BM_LOGIN_BUTTON)
    login_button.click()

    # go to scrape url
    browser.get(page_url)

    refresh_button = checkForElement(browser, lfc.BM_REFRESH_BUTTON)

    date_input = checkForElement(browser, lfc.BM_DATE_FIELD)
    date_input.clear()
    todays_date = '3/20/2016'
    date_input.send_keys(todays_date)
    refresh_button.click()

    # print (browser.current_url)

    # find select all game box (when loaded) and click
    select_all = checkForElement(browser, lfc.BM_SELECT_ALL)
    # select_all = browser.find_element_by_name(lfc.BM_SELECT_ALL)
    # select_all = browser.find_element_by_xpath('//*[@id="form1"]/div[4]/div[2]/table/tbody/tr/td[1]/table/tbody/tr/td/p[2]/input[1]')
    select_all.click()


    # print (browser.current_url)

    # find refresh data button (when loaded) and click
    refresh_button = checkForElement(browser, lfc.BM_REFRESH_BUTTON)
    refresh_button.click()

    # print (browser.current_url)

    # print (browser.page_source)
    # get html tree from page
    tree = html.fromstring(browser.page_source)

    # # clean up
    browser.quit()
    display.stop()

    return tree


def extractProjectedStats(tree):

    # create dict to hold projections
    projection_dict = {}

    # for each row of player data in data table
    for data in tree.cssselect('table.gridThighlight tr'):

        # if row is a header row, skip it
        if (data[2].text_content()) == "Rank":
            pass
        # if not, extract data from row
        else:
            # select name row
            name_row = data.cssselect('td.tdl a')
            # print (name_row)

            # get data from each row's td's
            source_id = str(name_row[0].get('href')).split('=')[1]
            # print (source_id)
            name = name_row[0].text_content()
            pts = float(data[13].text_content())
            reb = float(data[15].text_content())
            ast = float(data[16].text_content())
            stl = float(data[17].text_content())
            blk = float(data[18].text_content())
            tpt = float(data[14].text_content())
            tov = float(data[21].text_content())
            mins = float(data[11].text_content())

            # get universal player id from player_data
            player_id = ps.getPlayerId(source_id, 3, name)

            # if no player_id found, player will be added to queue
            if player_id is None:
                # pass on data entry, do not add proj data for this player
                pass

            entry = ds.createEntry(pts, reb, ast, stl, blk, tov, tpt, mins)

            ds.addEntryToProjectionDict(projection_dict, player_id, entry)

    return projection_dict

tree = getHtmlTreeFromPage(lfc.BM_LOGIN_URL, lfc.BM_USER, lfc.BM_PW, lfc.BM_SCRAPE_URL)

stats = extractProjectedStats(tree)

print(json.dumps(stats))

counter = 0

for stat in stats:
    counter += 1

print(counter)
