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

    def __init__(self, gameDate, startTime, dayOfWeek, awayTeamId, homeTeamId, gameSlug):
        self.gameDate = gameDate
        self.startTime = startTime
        self.dayOfWeek = dayOfWeek
        self.awayTeamId = awayTeamId
        self.homeTeamId = homeTeamId,
        self.gameSlug = gameSlug

    def getCsvRow(self):
        return [
            self.gameDate,
            self.startTime,
            self.dayOfWeek,
            self.awayTeamId,
            self.homeTeamId,
            self.gameSlug
        ]

    def getTuple(self):
        return (
            self.gameDate,
            self.startTime,
            self.dayOfWeek,
            self.awayTeamId,
            self.homeTeamId,
            self.gameSlug
        )