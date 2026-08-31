class RewardFunction:
    def __init__(self, hit=10, miss=-1, false_alarm=-3, switch=-0.5):
        self.hit = hit
        self.miss = miss
        self.false_alarm = false_alarm
        self.switch = switch

    def calculate(self, is_hit, is_miss, is_false_alarm, did_switch):
        r = 0
        if is_hit: r += self.hit
        if is_miss: r += self.miss
        if is_false_alarm: r += self.false_alarm
        if did_switch: r += self.switch
        return r
