class NbaProjection:
    """
    Class for to insert projection into db
    Attrs: player_id, game_id, team_id, source_id
    ctd: mins, pts, reb, ast, stl, blk, tpt, tov, 
    """

    def __init__(self, gameDate, dayOfWeek, startTime, awayTeamId, homeTeamId):
        self.gameDate = gameDate
        self.dayOfWeek = dayOfWeek
        self.startTime = startTime
        self.awayTeamId = awayTeamId
        self.homeTeamId = homeTeamId