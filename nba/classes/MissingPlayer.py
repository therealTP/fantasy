class MissingPlayer:
    """
    Players that are in projection scrapes but no matching playerId
    Includes source id, id for that source, and player name to match
    """
    def __init__(self, sourceId, playerId, playerName):
        self.sourceId = sourceId
        self.playerId = playerId
        self.playerName = playerName