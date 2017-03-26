import requests
from lxml import html
import PlayerSuite as ps
import DataSuite as ds
import linksFilesCreds as lfc

def createGameDateUrl(game_date):
    """
    Takes in YYYY-MM-DD date string
    Creates formatted url to scrape from string
    Returns url
    """
    # create full date url to get data from
    base_url = lfc.BR_BASE_URL
    date_array = game_date.split('-')
    date_url = ('?month=' + date_array[1] + '&day=' + date_array[2] + '&year=' + date_array[0])
    full_url = base_url + date_url

    return full_url

def extractStatsFromHtml(html_string):
    """
    Takes in string of html to extract data from
    Creates HTML object out of it and pulls relevant data
    Returns dict of player data actual stats
    """
    # dict to hold all stat entries
    stats_dict = {}
    # convert to html object
    tree = html.fromstring(html_string)
    # extract rows
    rows = tree.cssselect('table#stats tbody tr')

    # for each row:
    for entry in rows:
        # if header row, skip
        if entry[0].text_content() == "Rk":
            pass

        # if not a header, extract stats from row and add to stats_dict
        else:
            slug = str(entry[1].cssselect('a')[0].get('href')) \
                   .split('/')[3].replace(".html", "")
            name = entry[1].text_content()
            player_id = ps.getPlayerId(slug, 5, name)

            # get all relevant stats
            pts = float(entry[24].text_content())
            reb = float(entry[18].text_content())
            ast = float(entry[19].text_content())
            stl = float(entry[20].text_content())
            blk = float(entry[21].text_content())
            tpt = float(entry[10].text_content())
            tov = float(entry[22].text_content())

            # parse mins into float
            time_array = entry[6].text_content().split(':')
            raw_mins = float(time_array[0])
            sec_in_decimal = int(time_array[1]) / 60
            mins = round(raw_mins + sec_in_decimal, 2)

            # generate entry for player stat
            entry = ds.createEntry(pts, reb, ast, stl, blk, tov, tpt, mins)
            # add entry to dict
            ds.addEntryToProjectionDict(stats_dict, player_id, entry)

    return stats_dict

def getStatsForDate(game_date):
    """
    Optional game date in YYYY-MM-DD format
    Default is yesterday
    Uses basketball-reference.com
    Returns all stats in dict
    """
    # create full date url to get data from
    full_url = createGameDateUrl(game_date)

    # get page from url & turn into html tree
    with requests.Session() as c:
        # page = c.get(full_url, headers=lfc.BR_HEADER, proxies = lfc.BR_PROXY)
        page = c.get(full_url, headers=lfc.BR_HEADER)
        stats_dict = extractStatsFromHtml(page.text)

    return stats_dict

def getStatsForDateArr(date_arr):
    """
    Takes in arr of date strings YYYY-MM-DD
    uses same session to scrape data for all dates
    Returns dict with keys as dates, stats as vals
    """
    # create empty dict
    final_dict = {}

    # open single requests session
    with requests.Session() as c:
        # for each date in date arr
        for date_str in date_arr:
            # create full date url to get data from
            full_url = createGameDateUrl(date_str)

            # get page html string
            page = c.get(full_url, headers=lfc.BR_HEADER)

            # extract stats from html string
            stats_dict = extractStatsFromHtml(page.text)

            # add stats for date to final dict
            final_dict[date_str] = stats_dict

            # print ("data scraped for ", date_str)

    return final_dict

# print (getStatsForDateArr(['2016-01-15', '2016-01-16', '2016-01-17']))
# print (getStatsForDate('2016-01-15'))
