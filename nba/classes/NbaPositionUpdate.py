class NbaPositionUpdate:
    """
    Class to update existing player's position
    """

    def __init__(self, playerId, newPosition):
        self.playerId = playerId
        self.newPosition = newPosition