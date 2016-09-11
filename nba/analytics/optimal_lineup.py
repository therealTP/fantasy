# create FinalProjection class in separate file
import PlayerSuite as ps
import DataSuite as ds
import s3
import linksFilesCreds as lfc
from FinalProjection import FinalProjection

def addSourceProjsToDict(source, sourceProjs, dict):
    """
    takes source projs for day from one source (nf, bm, etc)
    check if id in dict already & add, or add id & proj
    calculates final points proj & optimizes
    """
    for player_id, proj in sourceProjs.items():
        pointsProj = round(ds.getFinalPoints(proj, 'fanduel'), 3) # only do dk for now
        # try to add point projections to
        try:
            dict[player_id][source] = pointsProj
        except KeyError:
            dict[player_id] = {source: pointsProj}

def getFinalProjsForDay(dateStr):
    """
    will take in date str in YYYY-MM-DD format and pull raw projs for that date
    will go through each projection, calculate final points projection
    return dict of all players final point projs
    """

    # get raw projections for date
    rawProjs = s3.getObjectS3(lfc.AWS_BUCKET_NAME, lfc.PROJECTIONS_FOLDER + dateStr + '.json')

    # blank dict to hold final projs
    playerProjs = {} # id: {fp_proj: 20.40, bm_proj: 21.95, rw_proj: 22.19, nf_proj: 20.32}

    # add player projected points from each source to playerProjs
    nfProjs = rawProjs["number_fire"]["projections"]
    addSourceProjsToDict("nf", nfProjs, playerProjs)

    bmProjs = rawProjs["basketball_monster"]["projections"]
    addSourceProjsToDict("bm", bmProjs, playerProjs)

    fpProjs = rawProjs["fantasy_pros"]["projections"]
    addSourceProjsToDict("fp", fpProjs, playerProjs)

    rwProjs = rawProjs["roto_wire"]["projections"]
    addSourceProjsToDict("rw", rwProjs, playerProjs)

    # weighted/ averaged player projs
    finalProjs = {}

    # get average projection for each set of projections in playerProjs
    for player_id, projObj in playerProjs.items():
        projCount = 0
        projTotal = 0
        for source, proj in projObj.items():
            projCount += 1
            projTotal += proj

        # calculate average projection for each projObj, round to 3 digits
        finalProjs[player_id] = round(projTotal / projCount, 3)

    return finalProjs



def addPosAndSalaryData(playerProjsDict, dateStr):
    """
    Take in dict of final player projs
    Add pos and salary data for each player
    Return arr with pos, salary, name data, ready for knapsack problem
    """
    # get player data for ids and positions
    playerData = ps.getPlayerList()

    # get salary data for date
    salaries = s3.getObjectS3(lfc.AWS_BUCKET_NAME, lfc.SALARIES_FOLDER + 'fanduel_salaries.json')[dateStr]

    # create empty arr for final player projs
    finalProjs = []

    for player_id, proj in playerProjsDict.items():
        try:
            salary = int(salaries[player_id]["fanduel"])
            name = playerData[player_id]["name"]
            pos = playerData[player_id]["pos"]
            finalProj = FinalProjection(player_id, pos, name, salary, proj)
            finalProjs.append(finalProj)
        except KeyError:
            pass

    return finalProjs



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

    playerData.sort(key=lambda x: x.value, reverse=True)
    team = []

    for player in playerData:
        nam = player.name
        pos = player.position
        sal = player.salary
        pts = player.points
        if counts[pos] < constraints[pos] and current_team_salary + sal <= salaryCap:
            team.append(player)
            counts[pos] = counts[pos] + 1
            current_team_salary += sal
            continue
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

    playerData.sort(key=lambda x: x.points, reverse=True)
    for player in playerData:
        nam = player.name
        pos = player.position
        sal = player.salary
        pts = player.points
        if player not in team:
            pos_players = [ x for x in team if x.position == pos]
            pos_players.sort(key=lambda x: x.points)
            for pos_player in pos_players:
                if (current_team_salary + sal - pos_player.salary) <= salaryCap and pts > pos_player.points:
                    team[team.index(pos_player)] = player
                    current_team_salary = current_team_salary + sal - pos_player.salary
                    break
    return team

def getActualPointsForTeam(teamArr, dateStr):
    """
    Takes in team arr, which is arr of finalProjection objects
    Gets actual stats for each player on team & calculates points scored
    Returns points scored
    """
    # get raw projections for date
    actualStats = s3.getObjectS3(lfc.AWS_BUCKET_NAME, lfc.STATS_FOLDER + dateStr + '_actual.json')
    actualTeamPoints = 0
    for playerObj in teamArr:
        actualPlayerStats = actualStats[playerObj.player_id]
        actualPlayerPoints = ds.getFinalPoints(actualPlayerStats, 'fanduel')
        actualTeamPoints += actualPlayerPoints

    return actualTeamPoints

datesToTest = ds.getDateRangeArr('2015-11-04', '2016-04-05')

totalTested = 0
totalOver265 = 0
totalUnder275 = 0

for dateToTest in datesToTest:

    try:
        playerProjs = getFinalProjsForDay(dateToTest)
        finalProjs = addPosAndSalaryData(playerProjs, dateToTest)
        team = getOptimalLineup(finalProjs, 60000)
        points = 0
        salary = 0
        for player in team:
            points += player.points
            salary += player.salary
        actualPoints = getActualPointsForTeam(team, dateToTest)
        totalTested += 1
        if actualPoints > 275:
            totalOver265 += 1

        print(points, actualPoints)
    except (KeyError, TypeError):
        pass

print(totalOver265 / totalTested)



#     print (player)
# print ("\nPoints: {}".format(points))
# print ("Salary: {}".format(salary))
