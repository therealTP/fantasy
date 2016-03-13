from pyvirtualdisplay import Display
from selenium import webdriver
from lxml import html
import DataSuite as ds
import PlayerSuite as ps
import linksFilesCreds as lfc

def getHtmlTreeFromPage(login_url, user, pw, page_url):
    """
    Takes in params, sets up selenium browser
    Gets data via browser, closes browser
    Returns HTML tree w/ data
    """
    # open a virtual display to run on python anywhere
    display = Display(visible=0, size=(800, 600))
    display.start()

    # create selenium browser
    browser = webdriver.Firefox()
    browser.get(login_url)

    # pass
    username = browser.find_element_by_name('username')
    password = browser.find_element_by_name('password')

    username.send_keys(user)
    password.send_keys(pw)

    form = browser.find_element_by_class_name('form-horizontal')
    form.submit()

    browser.get(page_url)

    # print (browser.page_source)

    tree = html.fromstring(browser.page_source)

    # clean up
    browser.quit()
    display.stop()

    return tree


def extractProjectedStats(tree):
    """
    Create tree of HTML from page
    Extract relevant data from tree
    Compile/ return projection dict
    """
    # create dict to hold projections
    projection_dict = {}

    # create array of all rows in table body
    for data in tree.cssselect('table#data tbody tr'):
        # print (data)
        # get name and slug values (slug is ID for fp)
        name_cell = data.cssselect('a')[0]
        slug = str(name_cell.get('href'))[13:].replace('.php', '')
        name = str(name_cell.text_content())

        # extract values of relevant tds in row
        pts = float(data[2].text_content())
        reb = float(data[3].text_content())
        ast = float(data[4].text_content())
        stl = float(data[6].text_content())
        blk = float(data[5].text_content())
        tpt = float(data[9].text_content())
        tov = float(data[12].text_content())
        mins = float(data[11].text_content())

        # get player id for player, or add new entry to player dict with info
        player_id = ps.getPlayerId(slug, 4, name)

        # if no player id:
        if player_id is None:
            # pass on data entry, do not add proj data for this player
            pass
            # entry for the unfound id added to queue

        entry = ds.createEntry(pts, reb, ast, stl, blk, tov, tpt, mins)

        # print (slug + ": " + str(entry))

        ds.addEntryToProjectionDict(projection_dict, player_id, entry)

    return projection_dict

# tree = getHtmlTreeFromPage(lfc.FP_LOGIN_URL, lfc.FP_USER, lfc.FP_PW, lfc.FP_SCRAPE_URL)
# # print(tree)
# print(extractProjectedStats(tree))