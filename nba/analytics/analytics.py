import s3
import DataSuite as ds

projections = s3.getObjectS3('nba-data-2015-2016', 'daily-projections/2015-12-07.json')
actual = s3.getObjectS3('nba-data-2015-2016', 'actual-stats/2015-12-07_actual.json')

projCount = 0
errorTotal = 0
actTotal = 0
apeTotal = 0
weightedErrTotal = 0

for player_id, proj in projections["number_fire"]["projections"].items():
    try:
        nfProj = ds.getFinalPoints(proj, 'draftkings')
        pointsAct = ds.getFinalPoints(actual[player_id], 'draftkings')
        # exclude players that scored negative points
        if (nfProj < 12 or pointsAct < 0):
            pass
        else:
            fpProj = getFinalPoints(projections["fantasy_pros"]["projections"][player_id], 'draftkings')
            rwProj = getFinalPoints(projections["roto_wire"]["projections"][player_id], 'draftkings')
            bmProj = getFinalPoints(projections["basketball_monster"]["projections"][player_id], 'draftkings')
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
