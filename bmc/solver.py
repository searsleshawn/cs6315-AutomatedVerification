from z3 import Solver, Bool, sat

class BMCSolver:
    """
    Wrapper around the Z3 SMT solver used for bounded model checking.
    This abstraction hides solver syntax and provides minimal helper methods.
    """
    def __init__(self):
        # Initialize a new Z3 solver instance
        self.solver = Solver()

    def add(self, constraint):
        """Add a constraint (Z3 expression) to the solver."""
        self.solver.add(constraint)

    def check(self):
        """
        Run the solver and return True if the constraints are satisfiable (SAT),
        meaning a valid execution trace exists.
        """
        result = self.solver.check()
        return result == sat

    def model(self):
        """Return the satisfying model (state assignments) if SAT."""
        return self.solver.model()
