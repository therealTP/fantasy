import requests
from lxml import html
from dateutil import parser
# from nba.classes.NbaGamePre import NbaGamePre

BASE_URL = 'http://www.basketball-reference.com/leagues/NBA_2016_games-'
URL_EXT = '.html'
MONTHS = ['october', 'november', 'december', 'january', 'feburary', 'march', 'april', 'may', 'june']
TABLE_ID = '#schedule'

def getGamesFromMonth(month, sesObj):
    """
    Takes in month str and requests session object
    """
    monthUrl = BASE_URL + month + URL_EXT
    page = sesObj.get(monthUrl)
    tree = html.fromstring(page.text)
    selector = 'table' + TABLE_ID + ' tbody tr'
    gameRows = tree.cssselect(selector)

    games = []

    for gameRow in gameRows:
        rawDayDate = gameRow[0].text_content()
        day = rawDayDate[:3]
        rawDate = rawDayDate[4:]
        date = parser.parse(rawDate).strftime('%Y-%m-%d')
        print(day, date)
        # print (, gameRow[1].text_content(), gameRow[2].text_content(), gameRow[4].text_content())

# start session
session = requests.Session()

getGamesFromMonth(MONTHS[0], session)








