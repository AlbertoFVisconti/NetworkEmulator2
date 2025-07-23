# 🚀 Best Goodput Network Emulator

**Best Goodput** is a Python-based tool that emulates a Mininet network topology and configures it to achieve the **optimal overall goodput** under a given set of **flow demands**.

It parses a YAML configuration of routers, hosts, and traffic demands, computes the optimal flow routing using **linear programming (LP)**, and optionally starts a full Mininet emulation using the optimal setup.

---

## 📈 Objective

Given a set of flow demands between hosts, the tool:
- Computes the **best goodput** for each demand
- Maximizes the **minimum effectiveness ratio** across all flows:  
  \[
  \min_i \left( \frac{r_i^*}{r_i} \right)
  \]
- Outputs:
  - A **CPLEX LP** optimization model
  - The **optimized goodputs**
  - A **Mininet emulation** with optimal forwarding behavior

---

## 🧠 Example Visualization

![Optimized Routing Scheme](Immagine%202025-07-23%20235618.png)

---

## 📁 Files in This Repository

- `best_goodput.py` — Main Python script
- `topology.yaml` — Network topology and flow demands
- `lp_problem.lp` — CPLEX LP model output (optional)
- `lp_problem_sol.txt` — GLPK solution output
- `requirements.txt` — Required Python packages

---

## 🛠 Usage

```bash
sudo venv/bin/python3 best_goodput.py [options] topology.yaml
```

### Options

| Flag        | Description                                                        |
|-------------|--------------------------------------------------------------------|
| `-h`, `--help` | Show help message and exit                                       |
| `-p`, `--print` | Print the **best goodput** achieved for each flow and exit       |
| `-l`, `--lp` | Print the **LP formulation** (in CPLEX LP format) and exit        |

---

## 📘 Sample Outputs

### LP Generation

```bash
sudo venv/bin/python3 best_goodput.py --lp topology.yaml
```

**Output:**

```
Maximize
obj: ...
Subject to
...
End
```

---

### Goodput Summary

```bash
sudo venv/bin/python3 best_goodput.py --print topology.yaml
```

**Output:**

```
The best goodput for flow demand #1 is 8 Mbps  
The best goodput for flow demand #2 is 2 Mbps  
The best goodput for flow demand #3 is 10 Mbps  
```

---

## 🧮 Optimization Engine

- Uses [GLPK](https://www.gnu.org/software/glpk/) via `glpsol` to solve the LP model
- Parses solution from `lp_problem_sol.txt`
- MPLS rules are derived from solution and installed into the Mininet routers

---

## 🔧 Running the Emulator

Without any flags, the script launches a **Mininet emulation** with the optimal routing applied:

```bash
sudo venv/bin/python3 best_goodput.py topology.yaml
```

---

## 📦 Setup Instructions

### 1. Create a virtual environment

```bash
python3 -m venv venv
```

### 2. Activate and install dependencies

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Run the tool (requires sudo for Mininet)

```bash
sudo venv/bin/python3 best_goodput.py topology.yaml
```

---

## ✅ Assumptions

- Router and host names **do not** match `s[0-9]+` (reserved for auto-added switches)
- All links are point-to-point unless a subnet contains multiple hosts (switch auto-added)
- YAML input is guaranteed to be valid
- Costs (in Mbps) are consistent between adjacent interfaces
- All demands are between existing hosts

---

## 📘 References

- [GLPK / glpsol](https://www.gnu.org/software/glpk/)
- [Mininet](http://mininet.org/)
- [CPLEX LP Format](https://www.ibm.com/docs/en/icos/20.1.0?topic=representation-lp-format)
- *Computer Networking: A Top-Down Approach* — Kurose & Ross

---

## 👤 Author

Developed as an advanced networking project to explore optimization-based traffic engineering using Python, LP solvers, and emulation.
