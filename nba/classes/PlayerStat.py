class PlayerStat:
    """
    Class for actual stats objects
    To be scraped day after the game
    """
    
    def __init__(self, playerId, gameId, teamId, min, pts, reb, ast, stl, blk, tov, tpt):
        self.playerId = playerId
        self.gameId = gameId
        self.teamId = teamId
        self.min = min
        self.pts = pts
        self.reb = reb
        self.ast = ast
        self.stl = stl
        self.blk = blk
        self.tov = tov
        self.tpt = tpt

    def getCsvRow(self):
        return [
            self.playerId,
            self.gameId,
            self.teamId,
            self.min,
            self.pts,
            self.reb,
            self.ast,
            self.stl,
            self.blk,
            self.tov,
            self.tpt
        ]