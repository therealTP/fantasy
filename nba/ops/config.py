import os
import json

# this is set at the system level in ENV vars
configLocation = os.environ.get('NBA_CONFIG')

with open(configLocation) as config_file:
    appConfig = json.load(config_file)