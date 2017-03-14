# MODULE TO ACCESS LOCAL CONSTANTS IN JSON-DATA FOLDER
import definitions
import os
import json

# base path where all json data lives
BASE_JSON_DATA_PATH = os.path.join(definitions.ROOT_DIR, 'nba/json-data/')

# team abbrev to id json
TEAM_ABBREV_TO_ID_PATH = os.path.join(BASE_JSON_DATA_PATH, 'team-abbrev-to-id.json')
with open(TEAM_ABBREV_TO_ID_PATH) as config_file:
    TEAM_ABBREV_TO_ID = json.load(config_file)