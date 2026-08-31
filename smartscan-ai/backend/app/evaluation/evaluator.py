class Evaluator:
    def __init__(self):
        self.results = []
        
    def add_result(self, result):
        self.results.append(result)
        
    def summarize(self):
        return {"total_evaluations": len(self.results)}
