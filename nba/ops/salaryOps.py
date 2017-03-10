import nba.ops.apiCalls as api
import json

def parseSalariesToArrOfObjs(site):
    '''
    Site: 'FAN_DUEL' or 'DRAFT_KINGS'
    '''
    with open('./../local-data/fanduel_salaries.json') as salaries:
        salary_data = json.load(salaries)

    salaries = []
    missingPlayers = ['1355']

    if site == 'FAN_DUEL':
        siteKey = "fanduel"
    elif site == 'DRAFT_KINGS':
        siteKey = "draftkings"

    for date, players in salary_data.items():
        for playerId, salaryObj in players.items():
            if playerId in missingPlayers:
                continue
            else:
                try:
                    salaryObj = {
                        "playerId": int(playerId),
                        "gameDate": date,
                        "salary": int(salaryObj[siteKey]),
                        "site": site
                    }

                    salaries.append(salaryObj)
                except ValueError:
                    continue

    print("# SALARIES", len(salaries))
    return salaries

print(api.postSalaries(parseSalariesToArrOfObjs("FAN_DUEL")))
        