import s3

projections = s3.getObjectS3('nba-data-2015-2016', 'daily-projections/2015-12-07.json')
actual = s3.getObjectS3('nba-data-2015-2016', 'actual-stats/2015-12-07_actual.json')

def getFinalPoints(pointsDict):
    """
    dk: pts: 1, 3pt: 0.5, reb: 1.25, ast: 1.5, stl: 2, blk: 2, tov: -0.5

    """
    points = pointsDict["pts"] * 1 + pointsDict["3pt"] * 0.5 + pointsDict["reb"] * 1.25 + pointsDict["ast"] * 1.5 + pointsDict["stl"] * 2 + pointsDict["blk"] * 2 + pointsDict["tov"] * -0.5

    return points

projCount = 0
errorTotal = 0
actTotal = 0
apeTotal = 0
weightedErrTotal = 0

for player_id, proj in projections["number_fire"]["projections"].items():
    try:
        nfProj = getFinalPoints(proj)
        pointsAct = getFinalPoints(actual[player_id])
        # exclude players that scored negative points
        if (nfProj < 12 or pointsAct < 0):
            pass
        else:
            fpProj = getFinalPoints(projections["fantasy_pros"]["projections"][player_id])
            rwProj = getFinalPoints(projections["roto_wire"]["projections"][player_id])
            bmProj = getFinalPoints(projections["basketball_monster"]["projections"][player_id])
            pointsProj = (nfProj + fpProj + rwProj + bmProj) / 4
            absError = abs(pointsProj - pointsAct)
            weightedErr = (absError / pointsAct) * 100 * pointsAct
            weightedErrTotal += weightedErr

            actTotal += pointsAct
            errorTotal += absError
            projCount += 1

        # pe = abs(pointsProj - pointsAct) / pointsAct
        # print(pe)

        # sumAct += actual[player_id]["pts"]
        # sumProj += proj["pts"]
        # sumErr += abs(proj["pts"] - actual[player_id]["pts"])
    except (KeyError, ZeroDivisionError) as e:
        pass

wmape = weightedErrTotal / actTotal
vwmape = errorTotal / actTotal # aka madMean
mape = apeTotal / projCount

print ("WMAPE:", wmape, "VWMAPE:", vwmape)
