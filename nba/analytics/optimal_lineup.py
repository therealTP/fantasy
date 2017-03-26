import nba.ops.apiCalls as api
import nba.ops.mlDataPrep as ml

# function to get optimal lineup from arr of player objects
def getOptimalLineup(playerData, salaryCap):
    """
    Takes in finalProjs playerData array of objs + salaryCap int
    Finds optimal lineup
    Returns optimal lineup
    """
    current_team_salary = 0
    constraints = {
        'PG':2,
        'SG':2,
        'SF':2,
        'PF':2,
        'C':1
        # 'G':1,
        # 'F':1,
        # 'UTIL': 1
        }

    counts = {
        'PG':0,
        'SG':0,
        'SF':0,
        'PF':0,
        'C':0
        # 'G':0,
        # 'F':0,
        # 'UTIL': 0
        }

    playerData.sort(key=lambda x: x["value"], reverse=True)
    team = []

    for player in playerData:
        nam = player["player_bref_id"]
        pos = player["player_position"]
        sal = player["salary"]
        pts = player["pred_pts"]
        if counts[pos] < constraints[pos] and current_team_salary + sal <= salaryCap:
            team.append(player)
            counts[pos] = counts[pos] + 1
            current_team_salary += sal
        # if counts['G'] < constraints['G'] and current_team_salary + sal <= salaryCap and pos in ['PG','SG']:
        #     team.append(player)
        #     counts['G'] = counts['G'] + 1
        #     current_team_salary += sal
        # if counts['F'] < constraints['F'] and current_team_salary + sal <= salaryCap and pos in ['SF','PF']:
        #     team.append(player)
        #     counts['F'] = counts['F'] + 1
        #     current_team_salary += sal
        # if counts['UTIL'] < constraints['UTIL'] and current_team_salary + sal <= salaryCap and pos in ['PG','SG','SF', 'PF', 'C']:
        #     team.append(player)
        #     counts['UTIL'] = counts['UTIL'] + 1
        #     current_team_salary += sal

    playerData.sort(key=lambda x: x["pred_pts"], reverse=True)
    for player in playerData:
        nam = player["player_bref_id"]
        pos = player["player_position"]
        sal = player["salary"]
        pts = player["pred_pts"]
        if player not in team:
            pos_players = [ x for x in team if x["player_position"] == pos]
            pos_players.sort(key=lambda x: x["pred_pts"])
            for pos_player in pos_players:
                if (current_team_salary + sal - pos_player["salary"]) <= salaryCap and pts > pos_player["pred_pts"]:
                    team[team.index(pos_player)] = player
                    current_team_salary = current_team_salary + sal - pos_player["salary"]
                    break
    return team

def getActualPointsForTeam(teamArr):
    """
    Takes in team arr, which is arr of finalProjection objects
    Gets actual stats for each player on team & calculates points scored
    Returns points scored
    """

    actualTeamPoints = 0
    for playerObj in teamArr:
        if playerObj["actual_pts"] == 0:
            print("NO POINTS FOR ", playerObj)
        actualTeamPoints += playerObj["actual_pts"]

    return actualTeamPoints

def getFinalAnalysisForDates(datesToTest, source, salaryCap, threshold):
    totalTested = 0
    totalOver = 0

    # for dates in range:
    for dateToTest in datesToTest:
        try:
            # get the predictions for the date
            playerProjs = api.getPredictions(source, dateToTest)
            # print(playerProjs[0].value)
            
            # calculate optimal lineup from predictions
            team = getOptimalLineup(playerProjs, salaryCap)
            
            predicted_points = 0
            team_salary = 0

            for player in team:
                predicted_points += player["pred_pts"]
                team_salary += player["salary"]

            # calculate actual pts for team
            actualPoints = getActualPointsForTeam(team)
            
            # inc totalOver count if team is over threshold
            if predicted_points > 0 and actualPoints > 0:
                print("DATE", dateToTest, "PREDICTED", predicted_points, "ACTUAL", actualPoints, "SALARY", team_salary)
                totalTested += 1
                if actualPoints > threshold:
                    totalOver += 1
            
        except (KeyError, TypeError):
            pass

    return float(totalOver / totalTested)

dates = ml.getDateRangeArr('2016-02-07', '2016-04-05')
source = 'GOOGLE'
cap = 60000
minimum = 285

print(getFinalAnalysisForDates(dates, source, cap, minimum))

