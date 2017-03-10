class PlayerUpdate:
    """
    Class to update player data, multiple times/day
    Injured, team, starting, depth, etc
    """

    def __init__(self, team, currentDepth, depthPos, isStarting, inactive, status):
        self.team = team
        self.currentDepth = currentDepth
        self.depthPos = depthPos
        self.isStarting = isStarting
        self.inactive = inactive
        self.status = status

    def getDict(self):
        return {
            "team": self.team,
            "currentDepth": self.currentDepth,
            "depthPos": self.depthPos,
            "isStarting": self.isStarting,
            "inactive": self.inactive,
            "status": self.status
        }