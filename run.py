#!/usr/bin/env python3
"""
Healthcare Access Optimization - Timor-Leste

Run this script to:
1. Generate the dataset
2. Build the optimization model
3. Solve and display results
"""
import json
import time
import os

from data_generator import generate_data
from inefficient_model import generate_gurobipy_model


def main():
    print("=" * 60)
    print("HEALTHCARE ACCESS OPTIMIZATION - TIMOR-LESTE")
    print("=" * 60)
    print()

    # Step 1: Generate data
    data_path = os.path.join(os.path.dirname(__file__), "large_data.json")

    if not os.path.exists(data_path):
        print("[1/3] Generating dataset...")
        generate_data(seed=42, output_path=data_path)
        print(f"      Dataset saved to {data_path}")
    else:
        print("[1/3] Loading existing dataset...")

    with open(data_path, 'r') as f:
        data = json.load(f)

    print(f"      Households: {len(data['households']):,}")
    print(f"      Existing hospitals: {len(data['existing_hospitals'])}")
    print(f"      Potential sites: {len(data['potential_hospitals'])}")
    print(f"      Max new hospitals: {data['max_new_hospitals']}")
    print()

    # Step 2: Build model
    print("[2/3] Building optimization model...")
    model = generate_gurobipy_model(data)
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
