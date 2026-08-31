class CostFunction:
    def __init__(self, w1=1.0, w2=1.0, w3=1.0, w4=0.1):
        self.w1 = w1 # delay
        self.w2 = w2 # Pfa
        self.w3 = w3 # 1-Pd
        self.w4 = w4 # switch

    def calculate(self, delay, pfa, pd, switches):
        return self.w1 * delay + self.w2 * pfa + self.w3 * (1 - pd) + self.w4 * switches
