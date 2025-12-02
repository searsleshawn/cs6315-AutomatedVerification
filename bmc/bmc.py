from z3 import Bool, And, Or, Not, Implies
from bmc.solver import BMCSolver

def run_bmc(ts, bound: int, target_state: str, safety: bool = False, verbose: bool = False):
    """
    Perform bounded model checking on a transition system.

    Semantics (core solver behavior):
      - Always checks reachability of `target_state` within the bound.
      - The `safety` flag DOES NOT change the encoding; it is only for
        the caller to interpret the result differently (e.g., as a
        safety violation if `target_state` is 'Error').

    Args:
        ts           : TransitionSystem object.
        bound        : Depth limit (k) for unrolling transitions.
        target_state : State to check reachability for.
        safety       : Ignored in encoding; used by caller to interpret SAT/UNSAT.
        verbose      : If True, prints detailed encoding steps for explanation/demo.

    Returns:
        (sat_result, trace)
        sat_result : True if there exists a path from init to target_state
                     within ≤ bound steps; False otherwise.
        trace      : List of visited states (length bound+1) if SAT, else None.
    """
    solver = BMCSolver()

    if verbose:
        print("\n=== Bounded Model Checking Encoding ===")
        print(f"Model: {ts.name}")
        print(f"Bound (k): {bound}")
        print(f"Initial State: {ts.init}")
        print(f"States: {ts.states}\n")

    # --- Step 1: State variables s_t ---
    states = {(s, t): Bool(f"{s}_{t}") for s in ts.states for t in range(bound + 1)}

    # --- Step 2: Initial condition: exactly init is true at t = 0 ---
    solver.add(And(
        states[(ts.init, 0)],
        *[Not(states[(s, 0)]) for s in ts.states if s != ts.init]
    ))

    if verbose:
        print("Initial condition:")
        print(f"  {ts.init}_0 = True, all other s_0 = False\n")

    # --- Step 3: Transition relation + exclusivity for t = 0..bound-1 ---
    for t in range(bound):
        if verbose:
            print(f"--- Step {t} → {t+1} ---")

        for s in ts.states:
            next_states = ts.transitions.get(s, [])
            if next_states:
                # Normal transition: if in s at t, must go to one of its successors at t+1
                if verbose:
                    print(f"Transition rule: {s}_{t} → "
                          f"{', '.join(f'{n}_{t+1}' for n in next_states)}")
                solver.add(Implies(
                    states[(s, t)],
                    Or(*[states[(nxt, t + 1)] for nxt in next_states])
                ))
            else:
                # Dead-end: if in s at t, must stay in s at t+1
                if verbose:
                    print(f"Dead-end rule: {s}_{t} → {s}_{t+1} (no outgoing transitions)")
                solver.add(Implies(
                    states[(s, t)],
                    states[(s, t + 1)]
                ))

        # Exclusivity at time t: exactly one state is true
        solver.add(Or(*[states[(s, t)] for s in ts.states]))
        for i, s1 in enumerate(ts.states):
            for s2 in ts.states[i + 1:]:
                solver.add(Or(Not(states[(s1, t)]), Not(states[(s2, t)])))

        if verbose:
            print("Exclusivity constraint at time", t,
                  ": exactly one state is true\n")

    # --- Exclusivity at final timestep t = bound ---
    solver.add(Or(*[states[(s, bound)] for s in ts.states]))
    for i, s1 in enumerate(ts.states):
        for s2 in ts.states[i + 1:]:
            solver.add(Or(Not(states[(s1, bound)]), Not(states[(s2, bound)])))

    # --- Step 4: Property encoding: reachability of target_state ---
    if target_state not in ts.states:
        # Cannot possibly reach a state that doesn't exist
        if verbose:
            print(f"Target state '{target_state}' not in model states → unreachable.\n")
        return False, None

    if verbose:
        print("\nProperty encoding (Reachability):")
        print(f"Check if '{target_state}' is reachable for some t ≤ {bound}\n")

    goal = Or(*[states[(target_state, t)] for t in range(bound + 1)])
    solver.add(goal)

    if verbose:
        print("=== Encoding complete. Sending to Z3 solver... ===\n")

    # --- Step 5: Solve and extract result ---
    sat_result = solver.check()

    if verbose:
        print("Solver result:", "SAT" if sat_result else "UNSAT")

    if not sat_result:
        return False, None

    model = solver.model()
    trace = extract_trace(states, model, ts, bound)

    if verbose:
        print("\nExtracted trace:")
        print(" → ".join(trace), "\n")

    return True, trace


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
