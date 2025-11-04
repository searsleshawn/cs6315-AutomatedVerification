from z3 import Solver, Bool, sat

class BMCSolver:
    def __init__(self):
        self.solver = Solver()

    def add(self, constraint):
        self.solver.add(constraint)

    def check(self):
        result = self.solver.check()
        return result == sat

    def model(self):
        return self.solver.model()
