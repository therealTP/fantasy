import os
import json
import sys
import definitions

with open(definitions.NBA_CONFIG_PATH) as config_file:
    APP_CONFIG = json.load(config_file)
