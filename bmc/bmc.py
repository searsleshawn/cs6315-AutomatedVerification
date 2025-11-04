from z3 import Bool, And, Or, Not, Implies
from bmc.solver import BMCSolver

def run_bmc(ts, bound: int, target_state: str, safety: bool = False):
    """
    Bounded Model Checker:
    - If safety=False → reachability: ∃ t ≤ k . target(t)
    - If safety=True  → safety: ∀ t ≤ k . ¬error(t)
    """
    solver = BMCSolver()

    # Encode states as Boolean variables for each time step
    states = { (s, t): Bool(f"{s}_{t}") for s in ts.states for t in range(bound + 1) }

    # Initial condition: only init true at t=0
    solver.add(And(states[(ts.init, 0)], *[Not(states[(s, 0)]) for s in ts.states if s != ts.init]))

    # Transition relation for each step
    for t in range(bound):
        for s in ts.states:
            next_states = ts.transitions.get(s, [])
            if next_states:
                solver.add(Implies(
                    states[(s, t)],
                    Or(*[states[(nxt, t + 1)] for nxt in next_states])
                ))

        # Exclusivity (exactly one state per time)
        solver.add(Or(*[states[(s, t)] for s in ts.states]))
        for s1 in ts.states:
            for s2 in ts.states:
                if s1 != s2:
                    solver.add(Or(Not(states[(s1, t)]), Not(states[(s2, t)])))

    # --- SAFETY OR REACHABILITY SECTION ---
    if safety:
        # Safety: add ¬error for all time steps
        if "error" in ts.states:
            for t in range(bound + 1):
                solver.add(Not(states[("error", t)]))
    else:
        # Reachability: target reachable within bound
        goal = Or(*[states[(target_state, t)] for t in range(bound + 1)])
        solver.add(goal)
    # --------------------------------------

    # Solve
    sat_result = solver.check()
    if sat_result:
        m = solver.model()
        trace = extract_trace(states, m, ts, bound)
        return sat_result, trace
    else:
        return sat_result, None


def extract_trace(states, model, ts, bound):
    trace = []
    for t in range(bound + 1):
        for s in ts.states:
            if model.evaluate(states[(s, t)], model_completion=True):
                trace.append(s)
                break
    return trace
