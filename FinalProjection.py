class FinalProjection():

    def __init__(self, player_id, position, name, salary, points):
        self.self = self
        self.player_id = player_id
        self.position = position
        self.name = name
        self.salary = salary
        self.points = points
        self.value = round(points / (salary / 1000), 3)

    # def __iter__(self):
    #     return iter(self.list)

    def __str__(self):
        return str(self.player_id) + " " + self.name + " " + self.position + " " + str(self.salary) + " " + str(self.points)
