class NbaGamePost:
    """
    Class to gather data about games after they are over
    Score, attendance, final Injured/DNPs
    """

    def __init__(self, gameId, awayTeamPts, homeTeamPts, awayTeamInjured, homeTeamInjured, attendance):
        self.gameId = gameId
        self.awayTeamPts = awayTeamPts
        self.homeTeamPts = homeTeamPts
        self.awayTeamInjured = awayTeamInjured
        self.homeTeamInjured = homeTeamInjured
        self.attendance = attendance

    def getDict(self):
        return {
            "gameId": self.gameId,
            "awayTeamPts": self.awayTeamPts,
            "homeTeamPts": self.homeTeamPts,
            "awayTeamInjured": self.awayTeamInjured,
            "homeTeamInjured": self.homeTeamInjured,
            "attendance": self.attendance
        }