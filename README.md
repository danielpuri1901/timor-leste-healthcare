# Healthcare Access Optimization — Timor-Leste

A set-cover MILP for placing new rural hospitals in Timor-Leste: pick which sites to build so the maximum population is within S kilometres of a hospital, given a limited budget and a rugged-terrain travel constraint.

## Accomplishments

Built by [Daniel Puri](https://github.com/danielpuri1901) as one of three MILP test problems used to design the eval harness for [`optimaze-agent`](https://github.com/danielpuri1901/optimaze-agent) — my open-source Gurobi auto-tuner. This formulation includes a **deliberate density inefficiency** (coverage constraints over infeasible household–hospital pairs) — the kind of structural pathology optimaze's tuning agent is designed to discover and fix.

- Set-cover variant over **2,000+ households, 15 existing hospitals, 50 potential sites**
- Drove the design of optimaze's **automated eval harness** over the MIPLIB benchmark suite — tracking solve time, optimality gap, and branch-and-bound nodes
- Helped optimaze achieve **up to 85% peak / 20–50% typical solve-time improvement** vs. default Gurobi configurations
- Optimaze was **presented to Gurobi's optimization team** and **received an acquisition offer (declined)**
- Distributed as a public **PyPI package** — [`optimaze`](https://pypi.org/project/optimaze/)

The other two test problems are [`mobian-optimization`](https://github.com/danielpuri1901/mobian-optimization) and [`uber-network-routing-demo`](https://github.com/danielpuri1901/uber-network-routing-demo).

## Problem

**Objective:** Maximize the number of people with access to a hospital within S kilometres.

### Key constraints
- Existing hospitals must remain operational
- Limited budget allows only `p` new hospitals
- Households must be within S km of an assigned hospital

## Scale

| Parameter | Value |
|---|---|
| Households | 2,000+ |
| Existing hospitals | 15 |
| Potential new sites | 50 |
| Max new hospitals | 10 |
| Max travel distance | 25 km |

## Mathematical formulation

### Sets
- **I**: households
- **J**: hospital locations (existing + potential)

### Parameters
- **p_i**: population of household i
- **d_ij**: distance from household i to hospital j
- **S**: maximum allowable travel distance
- **M**: number of existing hospitals
- **p**: maximum new hospitals to build

### Decision variables
- **x_j** ∈ {0,1}: 1 if hospital j is open
- **y_i** ∈ {0,1}: 1 if household i is covered

### Formulation

```
maximize    Σ(i) p_i · y_i

subject to:
            x_j = 1,  ∀j ∈ existing hospitals     (keep existing open)
            Σ(j ∈ new) x_j ≤ p                    (limit new hospitals)
            y_i ≤ Σ(j: d_ij ≤ S) x_j,  ∀i        (coverage needs nearby hospital)
            x_j, y_i ∈ {0,1}
```

### Deliberate inefficiency (test case for `optimaze-agent`)

The coverage constraints link every household to **all** potential hospitals, creating dense constraint matrices even when most hospital–household pairs are infeasible due to distance. The natural fix is to pre-filter by distance before generating constraints — exactly the kind of structural rewrite the optimaze tuning agent is designed to propose.

## Run it

```bash
pip install gurobipy
python run.py
```

Requires a working Gurobi licence ([free academic licence](https://www.gurobi.com/academia/academic-program-and-licenses/)).

## See also

- **[`optimaze-agent`](https://github.com/danielpuri1901/optimaze-agent)** — the open-source auto-tuner this problem helps test ([PyPI](https://pypi.org/project/optimaze/))
- **[`mobian-optimization`](https://github.com/danielpuri1901/mobian-optimization)** — Park & Bike hub location, ~672K vars
- **[`uber-network-routing-demo`](https://github.com/danielpuri1901/uber-network-routing-demo)** — Manhattan MDCVRPTW with 7 deliberate inefficiencies
