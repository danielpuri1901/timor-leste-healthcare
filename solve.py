#!/usr/bin/env python3
"""
Healthcare Access Optimization - Timor-Leste

Maximizes population coverage within reasonable travel distance by
optimizing placement of new hospitals.

Problem Scale:
- 20,000 households
- 15 existing hospitals
- 100 potential new sites
- Max 10 new hospitals
"""
import json
import time
import os

import gurobipy as gp


def generate_data(seed=42):
    """Generate synthetic healthcare placement data."""
    import random
    import numpy as np

    random.seed(seed)
    np.random.seed(seed)

    # Problem size parameters
    n = 20000  # Number of households
    m = 15     # Number of existing hospitals
    num_new_sites = 100  # Number of candidate hospital sites
    S = round(random.uniform(8, 15), 2)  # Max allowed travel distance (km)
    p = min(random.randint(5, num_new_sites), num_new_sites)

    # Sets (string IDs)
    households = [f"H{i+1}" for i in range(n)]
    existing_hospitals = [f"EJ{i+1}" for i in range(m)]
    candidate_hospitals = [f"CJ{i+1}" for i in range(num_new_sites)]
    all_hospitals = existing_hospitals + candidate_hospitals

    # Assign random coordinates
    household_coords = np.random.uniform(0, 100, size=(n, 2))
    hospital_coords = np.random.uniform(0, 100, size=(m + num_new_sites, 2))

    # Population per household
    population = {h: int(np.random.randint(50, 500)) for h in households}

    # Compute travel distances (Euclidean, rounded)
    travel_distances = {}
    for i, h in enumerate(households):
        travel_distances[h] = {}
        for j, hosp in enumerate(all_hospitals):
            dist = np.linalg.norm(household_coords[i] - hospital_coords[j])
            travel_distances[h][hosp] = round(float(dist + np.random.uniform(-10, 10)), 2)

    # Distance indicators (1 if within S, else 0)
    distance_indicators = {}
    for h in households:
        distance_indicators[h] = {}
        for hosp in all_hospitals:
            distance_indicators[h][hosp] = int(travel_distances[h][hosp] <= S)

    return {
        'households': households,
        'existing_hospitals': existing_hospitals,
        'candidate_hospitals': candidate_hospitals,
        'all_hospitals': all_hospitals,
        'population': population,
        'travel_distances': travel_distances,
        'distance_indicators': distance_indicators,
        'max_travel_distance': S,
        'max_new_hospitals': p
    }


def build_model(data):
    """
    Build the Timor-Leste healthcare optimization model.

    This model uses binary variables for each household-hospital assignment.
    The model is inefficient because it requires O(|I| * |J|) binary variables
    for detailed household-hospital assignments.
    """
    households = data["households"]
    existing_hospitals = data["existing_hospitals"]
    candidate_hospitals = data["candidate_hospitals"]
    all_hospitals = data["all_hospitals"]
    population = data["population"]
    distance_indicators = data["distance_indicators"]
    max_new_hospitals = data["max_new_hospitals"]

    # Create model
    model = gp.Model("TimorLeste_Healthcare")

    # Variables: x_j = 1 if hospital j is opened, 0 otherwise
    x = {}
    for j in all_hospitals:
        x[j] = model.addVar(vtype=gp.GRB.BINARY, name=f"x_{j}")

    # Variables: y_{ij} = 1 if demand at household i is served by hospital j
    y = {}
    for i in households:
        for j in all_hospitals:
            y[i, j] = model.addVar(vtype=gp.GRB.BINARY, name=f"y_{i}_{j}")

    # Objective: Maximize the number of people served
    objective = gp.quicksum(population[i] * y[i, j] for i in households for j in all_hospitals)
    model.setObjective(objective, gp.GRB.MAXIMIZE)

    # Constraint 1: Existing hospitals must remain open
    for j in existing_hospitals:
        model.addConstr(x[j] == 1, name=f"existing_hospital_{j}")

    # Constraint 2: At most p new hospitals can be opened
    model.addConstr(gp.quicksum(x[j] for j in candidate_hospitals) <= max_new_hospitals,
                   name="max_new_hospitals")

    # Constraint 3: People can only be assigned to opened facilities
    for j in all_hospitals:
        model.addConstr(gp.quicksum(y[i, j] for i in households) <= len(households) * x[j],
                       name=f"facility_open_{j}")

    # Constraint 4: Each household can be assigned to at most one hospital
    for i in households:
        model.addConstr(gp.quicksum(y[i, j] for j in all_hospitals) <= 1,
                       name=f"single_assignment_{i}")

    # Constraint 5: Assignment only allowed if distance is within limit (LAZY)
    for i in households:
        for j in all_hospitals:
            if distance_indicators[i][j] == 0:  # Only add constraint if distance exceeds limit
                model.addConstr(y[i, j] <= 0,
                               name=f"distance_limit_{i}_{j}", lazy=1)

    return model


def main():
    print("=" * 60)
    print("HEALTHCARE ACCESS OPTIMIZATION - TIMOR-LESTE")
    print("=" * 60)
    print()

    # Step 1: Load or generate data
    data_path = os.path.join(os.path.dirname(__file__), "large_data.json")

    if os.path.exists(data_path):
        print("[1/3] Loading existing dataset...")
        with open(data_path, 'r') as f:
            data = json.load(f)
    else:
        print("[1/3] Generating dataset...")
        data = generate_data(seed=42)
        with open(data_path, 'w') as f:
            json.dump(data, f)
        print(f"      Dataset saved to {data_path}")

    print(f"      Households: {len(data['households']):,}")
    print(f"      Existing hospitals: {len(data['existing_hospitals'])}")
    print(f"      Potential sites: {len(data['candidate_hospitals'])}")
    print(f"      Max new hospitals: {data['max_new_hospitals']}")
    print()

    # Step 2: Build model
    print("[2/3] Building optimization model...")
    model = gp.Model("TimorLeste_Healthcare")

    # Extract data
    households = data["households"]
    existing_hospitals = data["existing_hospitals"]
    candidate_hospitals = data["candidate_hospitals"]
    all_hospitals = data["all_hospitals"]
    population = data["population"]
    distance_indicators = data["distance_indicators"]
    max_new_hospitals = data["max_new_hospitals"]

    # Variables: x_j = 1 if hospital j is opened
    x = {}
    for j in all_hospitals:
        x[j] = model.addVar(vtype=gp.GRB.BINARY, name=f"x_{j}")

    # Variables: y_{ij} = 1 if household i is served by hospital j
    y = {}
    for i in households:
        for j in all_hospitals:
            y[i, j] = model.addVar(vtype=gp.GRB.BINARY, name=f"y_{i}_{j}")

    # Objective: Maximize people served
    objective = gp.quicksum(population[i] * y[i, j] for i in households for j in all_hospitals)
    model.setObjective(objective, gp.GRB.MAXIMIZE)

    # Constraint 1: Existing hospitals must remain open
    for j in existing_hospitals:
        model.addConstr(x[j] == 1, name=f"existing_hospital_{j}")

    # Constraint 2: At most p new hospitals can be opened
    model.addConstr(gp.quicksum(x[j] for j in candidate_hospitals) <= max_new_hospitals,
                   name="max_new_hospitals")

    # Constraint 3: People can only be assigned to opened facilities
    for j in all_hospitals:
        model.addConstr(gp.quicksum(y[i, j] for i in households) <= len(households) * x[j],
                       name=f"facility_open_{j}")

    # Constraint 4: Each household can be assigned to at most one hospital
    for i in households:
        model.addConstr(gp.quicksum(y[i, j] for j in all_hospitals) <= 1,
                       name=f"single_assignment_{i}")

    # Constraint 5: Assignment only allowed if distance is within limit
    for i in households:
        for j in all_hospitals:
            model.addConstr(y[i, j] <= distance_indicators[i][j],
                           name=f"distance_limit_{i}_{j}")

    print(f"      Variables: {model.NumVars:,}")
    print(f"      Constraints: {model.NumConstrs:,}")
    print(f"      Binary variables: {model.NumBinVars:,}")
    print()

    # Step 3: Solve
    print("[3/3] Solving...")
    print("-" * 60)

    start_time = time.time()
    model.optimize()
    solve_time = time.time() - start_time

    print("-" * 60)
    print()

    # Results
    print("RESULTS")
    print("=" * 60)

    if model.Status == 2:  # Optimal
        print(f"Status: Optimal")
        print(f"Objective: {model.ObjVal:,.0f} (people covered)")
        print(f"Solve time: {solve_time:.2f} seconds")
        print(f"Nodes explored: {int(model.NodeCount):,}")
    else:
        print(f"Status: {model.Status}")
        print(f"Solve time: {solve_time:.2f} seconds")

    print()


if __name__ == "__main__":
    main()
