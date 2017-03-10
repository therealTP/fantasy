import nba.ops.mlDataPrep as ml

trainDates = ml.getDateRangeArr('2015-11-04', '2016-01-25')
stat = 'tpt'

ml.pullAzureTrainingDataAndWriteToCsv(trainDates, stat)



