class AblationStudyRunner:
    def __init__(self, components):
        self.components = components
        
    def run(self, base_config):
        results = {}
        for comp in self.components:
            config = base_config.copy()
            config[comp] = False
            # run experiment
            results[comp] = {"status": "ablated"}
        return results
