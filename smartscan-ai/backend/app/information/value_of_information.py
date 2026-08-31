class VOICalculator:
    @staticmethod
    def calculate_voi(information_gain, cost):
        # VOI = Expected utility of information - cost
        return information_gain - cost
