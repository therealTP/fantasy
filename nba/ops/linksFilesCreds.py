# numberfire

NF_SCRAPE_URL = 'https://www.numberfire.com/nba/fantasy/full-fantasy-basketball-projections'
NF_CREDS = ('epistemconsulting@gmail.com', '9L2a8r8ry')
NF_TEAM_URL = 'https://www.numberfire.com/nba/teams/'

# rotowire

RW_LOGIN_URL = 'http://www.rotowire.com/users/loginuser2.htm'

RW_CREDS = {
    'username': 'mrtylerpalmer',
    'p1': '9L2a8r8ry',
    'submit': 'Login To Rotowire.com'
}

RW_SCRAPE_URL = 'http://www.rotowire.com/basketball/daily_projections.htm'

# basketball monster

BM_LOGIN_URL = 'https://basketballmonster.com/Login.aspx'
BM_USER = 'richardpalmer'
BM_PW = 'RVXYMDQKOZ'
# BM_HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1) \
# AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 \
# Safari/537.36"}

BM_SCRAPE_URL = 'https://basketballmonster.com/Daily.aspx'

# field names
BM_LOGIN_FIELD = 'ctl00$ContentPlaceHolder1$UsernameTextBox'
BM_PW_FIELD = 'ctl00$ContentPlaceHolder1$PasswordTextBox'
BM_LOGIN_BUTTON = 'ContentPlaceHolder1_LoginButton'
BM_DATE_FIELD = 'ctl00$ContentPlaceHolder1$StartDateTextBox'
# BM_UPDATE_BUTTON = 'UPDATEDATE'
BM_SELECT_ALL = 'SELECTALL'
BM_REFRESH_BUTTON = 'ctl00$ContentPlaceHolder1$RefreshButton'

# fantasy pros

FP_LOGIN_URL = 'https://secure.fantasypros.com/accounts/login/?next=http://www.fantasypros.com'
FP_SCRAPE_URL = 'http://www.fantasypros.com/nba/projections/avg-daily-overall.php'
FP_USER = 'tylerpalmerca'
FP_PW = 'larry25'

# bball reference (actual stats)
BR_BASE_URL = 'http://www.basketball-reference.com/friv/dailyleaders.cgi'
BR_PROXY = {"http": "http://38.103.38.120:80"}
BR_HEADER = {'User-agent': 'Mozilla/5.0'}

# fantasy cruncher: salaries and positions
FC_BASE_URL = 'https://www.fantasycruncher.com/lineup-rewind/'

# aws

AWS_ACCESS_KEY_ID = ''  # stored in config file
AWS_SECRET_ACCESS_KEY = ''  # stored in config file
AWS_BUCKET_NAME = 'nba-data-2015-2016'
PROJECTIONS_FOLDER = 'daily-projections/'  # same for internal & s3
STATS_FOLDER = 'actual-stats/'
SALARIES_FOLDER = 'salaries/'

# email

GMAIL_UN = 'tylerpalmerca@gmail.com'
GMAIL_PW = '9L2a8r8ry'
MAILTO = '3107669296@txt.att.net'
# MAILTO = 'mr.tylerpalmer@gmail.com'
SUBJECT = 'Daily Scraper Update'

# internal files

# DAILY_JSON_TEMPLATE = '/home/tylerpalmer/fantasy/json-data/projections_object_template.json'
# PLAYER_DATA = '/home/tylerpalmer/fantasy/json-data/player_data.json'
# PLAYER_ID_LOOKUP_JSON = '/home/tylerpalmer/fantasy/json-data/player_id_lookup.json'
# PLAYER_INFO_BY_NF_ID = '/home/tylerpalmer/fantasy/json-data/players_by_nf_id.json'
# PLAYER_QUEUE = '/home/tylerpalmer/fantasy/json-data/player_queue.json'

DAILY_JSON_TEMPLATE = './json-data/projections_object_template.json'
PLAYER_DATA = './json-data/player_data.json'
PLAYER_ID_LOOKUP_JSON = './json-data/player_id_lookup.json'
PLAYER_INFO_BY_NF_ID = './json-data/players_by_nf_id.json'
PLAYER_QUEUE = './json-data/player_queue.json'
