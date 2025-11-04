import argparse
from bmc.model import TransitionSystem
from bmc.bmc import run_bmc

def main():
    parser = argparse.ArgumentParser(description="Lightweight Bounded Model Checker")
    parser.add_argument("--model", required=True, help="Path to model JSON file")
    parser.add_argument("--bound", type=int, default=3, help="Bound for unrolling")
    parser.add_argument("--target", default="error", help="Target state to reach")
    # safety parse
    parser.add_argument("--safety", action="store_true", help="Check safety property instead of reachability")
    args = parser.parse_args()

    ts = TransitionSystem.from_json(args.model)
    print(f"\nLoaded model: {ts.name}")
    print(f"Initial state: {ts.init}, States: {ts.states}\n")

    # added safety arg
    # sat, model = run_bmc(ts, args.bound, args.target)
    sat, model = run_bmc(ts, args.bound, args.target, args.safety)
    # if sat:
    #     print(f"✅ Target state '{args.target}' is reachable within bound {args.bound}.")
    #     print("Model:")
    #     print(model)
    # if sat:
    #     print(f"✅ Target '{args.target}' reachable within bound {args.bound}.")
    #     print("Trace:", " → ".join(model))
    # else:
    #     print(f"❌ Target state '{args.target}' is NOT reachable within bound {args.bound}.")

    if sat:
        if args.safety:
            print(f"✅ Safety property holds: '{args.target}' is never reached within bound {args.bound}.")
        else:
            print(f"✅ Target '{args.target}' reachable within bound {args.bound}.")
            print("Trace:", " → ".join(model))
    else:
        if args.safety:
            print(f"❌ Safety property violated: '{args.target}' reached within bound {args.bound}.")
            print("Counterexample trace:", " → ".join(model or []))
        else:
            print(f"❌ Target state '{args.target}' is NOT reachable within bound {args.bound}.")


if __name__ == "__main__":
    main()
