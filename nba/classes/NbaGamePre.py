class NbaGamePre:
    """
    Class for objects containing data on games before they take place
    Used to insert new game data into db
    Attrs:
    -game_date
    -day_of_week
    -start_time (military ET)
    -home_team_id
    -away_team_id
    """

    def __init__(self, gameDate, dayOfWeek, startTime, awayTeamId, homeTeamId):
        self.gameDate = gameDate
        self.dayOfWeek = dayOfWeek
        self.startTime = startTime
        self.awayTeamId = awayTeamId
        self.homeTeamId = homeTeamId


    def getCsvRow(self):
        return [
            self.gameDate,
            self.dayOfWeek,
            self.startTime,
            self.homeTeamId,
            self.awayTeamId
        ]

    def getTuple(self):
        return (
            self.gameDate,
            self.dayOfWeek,
            self.startTime,
            self.homeTeamId,
            self.awayTeamId
        )