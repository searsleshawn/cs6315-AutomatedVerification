from z3 import Bool, And, Or, Not, Implies
from bmc.solver import BMCSolver

def run_bmc(ts, bound: int, target_state: str, safety: bool = False, verbose: bool = False):
    """
    Perform bounded model checking on a transition system.

    Args:
        ts           : TransitionSystem object.
        bound        : Depth limit (k) for unrolling transitions.
        target_state : State to check reachability or safety against.
        safety       : If True, checks safety (never reaches 'error');
                       otherwise checks reachability.
        verbose      : If True, prints detailed encoding steps for explanation/demo.

    Returns:
        (sat_result, trace)
        sat_result : True if the property holds (or target reachable).
        trace      : List of visited states (execution path).
    """
    solver = BMCSolver()

    # [VERBOSE] Header info
    if verbose:
        print("\n=== Bounded Model Checking Encoding ===")
        print(f"Model: {ts.name}")
        print(f"Bound (k): {bound}")
        print(f"Initial State: {ts.init}")
        print(f"States: {ts.states}\n")

    # === Step 1: Encode states ===
    # Each state s at each time step t ∈ [0..k] becomes a Boolean variable (s_t)
    states = {(s, t): Bool(f"{s}_{t}") for s in ts.states for t in range(bound + 1)}

    # === Step 2: Initial condition ===
    # Only the initial state is True at t = 0
    solver.add(And(states[(ts.init, 0)], *[Not(states[(s, 0)]) for s in ts.states if s != ts.init]))

    if verbose:
        print("Initial condition:")
        print(f"  {ts.init}_0 = True, others = False\n")

    # === Step 3: Transition relation ===
    for t in range(bound):
        if verbose:
            print(f"--- Step {t} → {t+1} ---")

        # Encode state transitions: if at state s at time t,
        # then at t+1 one of its successors must be active.
        for s in ts.states:
            next_states = ts.transitions.get(s, [])
            if next_states:
                if verbose:
                    print(f"Transition rule: {s}_{t} → {', '.join(f'{n}_{t+1}' for n in next_states)}")
                solver.add(Implies(
                    states[(s, t)],
                    Or(*[states[(nxt, t + 1)] for nxt in next_states])
                ))

        # Enforce exclusivity: exactly one state is True at each time step.
        solver.add(Or(*[states[(s, t)] for s in ts.states]))
        for s1 in ts.states:
            for s2 in ts.states:
                if s1 != s2:
                    solver.add(Or(Not(states[(s1, t)]), Not(states[(s2, t)])))

        if verbose:
            print("Exclusivity constraint: exactly one state true per timestep\n")

    # === Step 4: Property encoding ===
    if safety:
        if verbose:
            print("\nProperty encoding (Safety mode):")
            print("Ensure 'error' is False for all t ≤ k\n")
        bad_state = "Error" if "Error" in ts.states else "error" if "error" in ts.states else target_state
        goal = Or(*[states[(bad_state, t)] for t in range(bound + 1)])
        solver.add(goal)
    else:
        if verbose:
            print("\nProperty encoding (Reachability mode):")
            print(f"Check if '{target_state}' is reachable for any t ≤ {bound}\n")
        goal = Or(*[states[(target_state, t)] for t in range(bound + 1)])
        solver.add(goal)

    # [VERBOSE] End of encoding
    if verbose:
        print("=== Encoding complete. Sending to Z3 solver... ===\n")

    # === Step 5: Solve and extract result ===
    sat_result = solver.check()

    if verbose:
        print("Solver result:", "SAT" if sat_result else "UNSAT")

    if sat_result:
        model = solver.model()
        trace = extract_trace(states, model, ts, bound)
        if verbose:
            print("\nExtracted trace:")
            print(" → ".join(trace), "\n")
        return sat_result, trace
    else:
        return sat_result, None


def extract_trace(states, model, ts, bound):
    """
    Extracts a readable trace (list of active states over time)
    from the Z3 model that satisfied the constraints.
    """
    trace = []
    for t in range(bound + 1):
        for s in ts.states:
            if model.evaluate(states[(s, t)], model_completion=True):
                trace.append(s)
                break
    return trace
