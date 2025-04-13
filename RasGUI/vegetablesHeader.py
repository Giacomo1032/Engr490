class Vegetable:
    def __init__(self, name, growth_time, water_requirement, thresholds):
        self.name = name
        self.growth_time = growth_time  # in days
        self.water_requirement = water_requirement  # in liters per day
        self.thresholds = thresholds  # thresholds for variables like pH, Solution Level, etc.

    def __str__(self):
        return self.name


class Tomato(Vegetable):
    def __init__(self):
        thresholds = {
            "PH": {"low": 5.5, "medium": 6.0, "high": 6.5},
            "Solution Level": {"low": 20, "medium": 40, "high": 54},
            "TDS": {"low": 600, "medium": 800, "high": 1200},
            "DLI": {"low": 10, "medium": 20, "high": 30},
            "Turbidity": {"low": 0, "medium": 300, "high": 600},
        }
        super().__init__("Tomato", 70, 2, thresholds)


class Lettuce(Vegetable):
    def __init__(self):
        thresholds = {
            "PH": {"low": 5.5, "medium": 6.0, "high": 6.5},
            "Solution Level": {"low": 10, "medium": 30, "high": 60},
            "TDS": {"low": 400, "medium": 600, "high": 800},
            "DLI": {"low": 8, "medium": 16, "high": 25},
            "Turbidity": {"low": 0, "medium": 200, "high": 500},
        }
        super().__init__("Lettuce", 45, 1, thresholds)


class Cucumber(Vegetable):
    def __init__(self):
        thresholds = {
            "PH": {"low": 5.5, "medium": 6.0, "high": 6.5},
            "Solution Level": {"low": 20, "medium": 45, "high": 75},
            "TDS": {"low": 700, "medium": 1000, "high": 1400},
            "DLI": {"low": 5, "medium": 15, "high": 35},
            "Turbidity": {"low": 0, "medium": 400, "high": 700},
        }
        super().__init__("Cucumber", 60, 2.5, thresholds)
