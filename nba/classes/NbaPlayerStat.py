class NbaPlayerStat:
    """
    Class for actual stats objects
    To be scraped day after the game
    """
    
    def __init__(self, playerId, gameId, teamId, mins, pts, reb, ast, stl, blk, tpt, tov):
        self.playerId = playerId
        self.gameId = gameId
        self.teamId = teamId
        self.mins = mins
        self.pts = pts
        self.reb = reb
        self.ast = ast
        self.stl = stl
        self.blk = blk
        self.tpt = tpt
        self.tov = tov
