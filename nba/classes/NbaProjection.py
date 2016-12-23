class NbaProjection:
    """
    Class for to insert projection into db
    Attrs: player_id, game_id, team_id, source_id
    ctd: playerId, gameId, sourceId, mins, pts, reb, ast, stl, blk, tov, tpt 
    """

    def __init__(self, playerId, sourceId, mins, pts, reb, ast, stl, blk, tov, tpt):
        self.playerId = playerId
        self.sourceId = sourceId
        self.mins = mins
        self.pts = pts
        self.reb = reb
        self.ast = ast
        self.stl = stl
        self.blk = blk
        self.tov = tov
        self.tpt = tpt