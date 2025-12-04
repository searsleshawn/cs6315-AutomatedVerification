# Bounded Model Checker (CS6315 Final Project)
**Course:** CS 6315 – Automated Verification  
**Student:** Le’Shawn Sears  

---

## 🧠 Overview  

This project implements a **Lightweight Bounded Model Checker (BMC)** for verifying **finite-state systems** in Python 3.12 using the **Z3 SMT solver**.  
It supports both:

- **Reachability** — *Can the system ever reach a target state within k steps?*  
- **Safety** — *Can the system ever reach a bad (Error/error) state within k steps?*

The model checker produces **explicit symbolic traces**, making it easy to understand how Z3 constructs satisfying executions. This BMC is intentionally minimal and educational, showing how bounded unrolling, exclusivity constraints, and symbolic encoding work in practice.

---

## ⚙️ Architecture  

| File | Description |
|------|--------------|
| **`model.py`** | Defines the `TransitionSystem` dataclass and loads models from JSON. |
| **`solver.py`** | Lightweight wrapper (`BMCSolver`) around Z3’s `Solver`. |
| **`bmc.py`** | Core BMC algorithm: Boolean time-unwound variables, transitions, exclusivity, reachability, and safety checking. |
| **`main.py`** | CLI for running the BMC on any model file. |
| **`/examples/`** | JSON models demonstrating nondeterminism, dead ends, deep chains, and safety violations. |
| **`bmc-report.ipynb`** | comprehensive demonstration of the BMC pipeline end-to-end, including model loading, and analysis of edge-case systems. |

---

## 📦 Installation  

```bash
pip install -r requirements.txt
```

Or manually:

```bash
pip install z3-solver
```

---

## ▶️ Running the Model Checker From CLI  

### **Reachability Example**

```bash
python -m bmc.main --model examples/toggle.json --bound 5 --target s1
```

### **Safety Example**

```bash
python -m bmc.main --model examples/traffic.json --bound 5 --target Error --safety
```

### **Verbose Encoding**

```bash
python -m bmc.main --model examples/toggle.json --bound 3 --target s1 --verbose
```

---

## 📘 Example JSON Model Format  

```json
{
  "name": "ToggleSystem",
  "states": ["s0", "s1"],
  "init": "s0",
  "transitions": {
    "s0": ["s1"],
    "s1": ["s0"]
  }
}
```

---

## 🔍 Reachability Checking  

In reachability mode, the BMC checks:

> **Does there exist a timestep 0 ≤ t ≤ k such that `target_state_t` is true?**

Example:

```
Toggle reachability(s1): True ['s0', 's1', 's0', 's1', 's0', 's1']
```

A **SAT** result means a valid execution exists; the trace shows Z3's chosen path.

---

## 🚨 Safety Checking  

In safety mode, the checker searches for **a violation**:

> **Is an error state reachable within the bound?**

Example:

```
Safety violated: Error reachable.
Trace: ['Green', 'Yellow', 'Red', 'Error', 'Error', 'Error']
```

If **sat=True**, the system violates the safety property.

---

## 🧪 Edge Case Testing  

### ✔️ NondetExplosion  
High branching factor:

```
Reachability: SAT
Safety: Trivially safe (no error state)
```

### ✔️ DeepChain  
Long chain ending in error:

```
Reachability(error): SAT
Safety violated
```

### ✔️ DeadEndExample  

```
Reachability(goal): SAT
Safety: Safe (no error)
```

### ✔️ CycleWithError  

```
Reachability(Error): SAT
Safety violated
```

---

## 🧩 Internal BMC Operation Summary  

1. **Boolean Variable Expansion**  
2. **Initial State Constraint**  
3. **Transition Relation Encoding**  
4. **Exclusivity at Each Timestep**  
5. **Property Encoding (Reachability / Safety)**  

---

## 📈 Observations on Scalability  

- Runtime grows linearly with bound *k*  
- Branching factor heavily impacts solve time  
- Z3 handles deep deterministic chains well  
- Nondeterminism increases search complexity  

---

## 🧾 Conclusion  

This project demonstrates a clean, lightweight bounded model checker capable of solving realistic finite-state verification tasks.
