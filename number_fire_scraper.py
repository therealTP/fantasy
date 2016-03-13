import requests
from lxml import html
import DataSuite as ds
import linksFilesCreds as lfc
import PlayerSuite as ps

"""
NUMBERFIRE
"""

URL = lfc.NF_SCRAPE_URL
AUTH = lfc.NF_CREDS


def getFinalData(url, creds):
    """
    Takes in scrape_url, creds, search param
    Returns raw data in json format
    """

    # use requests module to hit URL
    r = requests.get(url, auth=creds)

    # get raw html from url
    raw_html = r.text

    tree = html.fromstring(raw_html)

    projection_dict = {}

    for dataRow in tree.cssselect('#projection-data tr'):
        # print (dataRow[0].cssselect('button')[0].get('rel'))
        player_link = dataRow.cssselect('td.player a')[0]
        slug = player_link.get('href').split('/')[-1]
        name = player_link.cssselect('span.full')[0].text_content().split(' (')[0]

        pts = float(dataRow[4].text_content())
        reb = float(dataRow[5].text_content())
        ast = float(dataRow[6].text_content())
        stl = float(dataRow[7].text_content())
        blk = float(dataRow[8].text_content())
        tpt = None
        tov = float(dataRow[9].text_content())
        mins = float(dataRow[3].text_content())

        player_id = ps.getPlayerId(slug, 1, name)

        if player_id is None:
            pass

        entry = ds.createEntry(pts, reb, ast, stl, blk, tov, tpt, mins)

        ds.addEntryToProjectionDict(projection_dict, player_id, entry)

    return projection_dict

# print(getRawData(URL, AUTH))
