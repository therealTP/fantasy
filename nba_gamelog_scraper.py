import requests
from lxml import html
import PlayerSuite as ps
import DataSuite as ds
import linksFilesCreds as lfc


def getStatsForDate(game_date):
    """
    Optional game date in YYYY-MM-DD format
    Default is yesterday
    Uses basketball-reference.com
    Returns all stats in dict
    """
    # create full date url to get data from
    base_url = lfc.BR_BASE_URL
    date_array = game_date.split('-')
    date_url = ('?month=' + date_array[1] + '&day=' +
                date_array[2] + '&year=' + date_array[0])
    full_url = base_url + date_url

    # get page from url & turn into html tree
    with requests.Session() as c:
        page = c.get(full_url, headers=lfc.BR_HEADER, proxies = lfc.BR_PROXY)
        tree = html.fromstring(page.text)

    # extract rows
    rows = tree.cssselect('table#stats tbody tr')

    # dict to hold all stat entries
    stats_dict = {}

    for entry in rows:
        # if header row, skip
        if entry[0].text_content() == "Rk":
            pass

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

# print (getStatsForDate('2015-11-16'))
