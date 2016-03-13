import requests
import PlayerSuite as ps
import DataSuite as ds
from lxml import html


def getHtmlTreeFromPage(login_url, creds, page_url):
    """
    Take in login URL/creds + page URL
    Convert to workable HTML tree
    Return HTML tree object
    """
    # Create Browser Session with requests to login to RW and pull data
    with requests.Session() as c:

        # Post login data to login form
        c.post(login_url, data=creds)

        # Get RAW HTML from projections page
        get_data = c.get(page_url)

        # Build HTML tree from raw HTML <text></text>
        tree = html.fromstring(get_data.text)

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
    for data in tree.cssselect('tbody tr.dproj-precise'):

        # extract values of relevant tds in rows

        # extract player_id
        source_id = str(data.cssselect('a')[0].get('href')).split('=')[1]

        # get raw name in array from span
        name_arr = str(data.cssselect('span')[0].text_content()).split('\xa0')
        name = str(name_arr[1]) + " " + str(name_arr[0])
        name = name.replace("  ", " ")

        # print (name)

        pts = float(data[5].text_content())
        reb = float(data[6].text_content())
        ast = float(data[7].text_content())
        stl = float(data[8].text_content())
        blk = float(data[9].text_content())
        tpt = float(data[10].text_content())
        tov = float(data[13].text_content())
        mins = float(data[4].text_content())

        # get player id for player, or add new entry to player dict with info
        player_id = ps.getPlayerId(source_id, 2, name)

        # if no player id:
        if player_id is None:
            # pass on data entry, do not add proj data for this player
            pass
            # entry for the unfound id added to queue

        entry = ds.createEntry(pts, reb, ast, stl, blk, tov, tpt, mins)

        ds.addEntryToProjectionDict(projection_dict, player_id, entry)

        # print (player_id)

    return projection_dict


def extractPlayerList():
    """
    Create tree of HTML from page
    Extract player list from tree
    Compile/ return projection dict
    """
    # create dict to hold projections
    player_list = []

    # extract/create tree
    tree = getHtmlTreeFromPage(LOGIN_URL, PAYLOAD, SCRAPE_URL)

    # create array of all rows in table body
    for data in tree.cssselect('tbody tr'):

        # extract values of relevant tds in rows
        name_array = data[0].text_content().split(u',\xa0')
        name = str(name_array[1]) + " " + str(name_array[0])

        player_list.append(name)

    return player_list
