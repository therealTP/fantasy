class NbaGameSpread:
    """
    """

    def __init__(self, gameId, awayPredPts, homePredPts):
        self.gameId = gameId
        self.awayPredPts = awayPredPts
        self.homePredPts = homePredPts
        self.homeSpread = awayPredPts - homePredPts
        self.total = awayPredPts + homePredPts