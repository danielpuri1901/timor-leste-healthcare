# Healthcare Access Optimization - Timor-Leste

## Problem Description

Timor-Leste faces significant challenges in ensuring equitable healthcare access, particularly in rural areas with challenging terrain. The government aims to optimize the placement of new hospitals to maximize population coverage within reasonable travel distances.

**Objective:** Maximize the number of people with access to a hospital within S kilometers.

### Key Constraints
- Existing hospitals must remain operational
- Limited budget allows only p new hospitals
- Households must be within S km of assigned hospital

## Problem Scale

| Parameter | Value |
|-----------|-------|
| Households | 2,000+ |
| Existing Hospitals | 15 |
| Potential New Sites | 50 |
| Max New Hospitals | 10 |
| Max Travel Distance | 25 km |

## Mathematical Formulation

### Sets
- **I**: Set of households
- **J**: Set of hospital locations (existing + potential)

### Parameters
- **p_i**: Population of household i
- **d_ij**: Distance from household i to hospital j
- **S**: Maximum allowable travel distance
- **M**: Number of existing hospitals
- **p**: Maximum new hospitals to build

### Decision Variables
- **x_j** ∈ {0,1}: 1 if hospital j is open
- **y_i** ∈ {0,1}: 1 if household i is covered

### Formulation

```
maximize    Σ(i) p_i · y_i

subject to:
            x_j = 1,  ∀j ∈ existing hospitals       (keep existing open)

            Σ(j ∈ new) x_j ≤ p                      (limit new hospitals)

            y_i ≤ Σ(j: d_ij ≤ S) x_j,  ∀i          (coverage requires nearby hospital)

            x_j, y_i ∈ {0,1}
```

### Why This Formulation Is Inefficient

The coverage constraints link every household to all potential hospitals, creating dense constraint matrices even when most hospital-household pairs are infeasible due to distance.

## Usage

```bash
python run.py
```
