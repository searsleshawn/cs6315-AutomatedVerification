# Bounded Model Checker (CS6315 Final Prject)
**Course:** CS 6315 – Automated Verification  
**Student:** Le’Shawn Sears    
---

## 🧠 Overview  

This project implements a **Lightweight Bounded Model Checker (BMC)** for verifying **finite-state systems** in Python 3.12 using the **Z3 SMT solver**.  
It supports both **reachability** and **safety** property analysis and provides clear, symbolic traces showing how states evolve over time.  

The goal is to create an educational, transparent verifier that illustrates symbolic reasoning, transition unrolling, and bounded verification using minimal dependencies.  

---

## ⚙️ Architecture  

| File | Description |
|------|--------------|
| `model.py` | Defines the `TransitionSystem` dataclass and loads models from JSON. |
| `solver.py` | Lightweight wrapper (`BMCSolver`) around the Z3 SMT solver. |
| `bmc.py` | Core BMC algorithm with transition encoding, exclusivity, reachability, and safety handling. |
| `main.py` | Command-line interface for running reachability or safety checks. |
| `/examples/` | Contains sample JSON models demonstrating different behaviors. |


