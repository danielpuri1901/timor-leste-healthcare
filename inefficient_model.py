import gurobipy as gp
from typing import Dict, List

def generate_gurobipy_model(data: Dict) -> gp.Model:
    """
    Generate the inefficient Timor-Leste model.
    
    This model uses binary variables for each household-hospital assignment.
    The model is inefficient because it requires O(|I| * |J|) binary variables
    for detailed household-hospital assignments.
    
    Args:
        data: Dictionary containing the dataset with keys:
            - households: List[str] - Set of household identifiers
            - existing_hospitals: List[str] - Set of existing hospital identifiers
            - candidate_hospitals: List[str] - Set of candidate hospital identifiers
            - all_hospitals: List[str] - Combined set of all hospital sites
            - population: Dict[str, int] - Number of people in each household
            - travel_distances: Dict[str, Dict[str, float]] - Travel distance from household i to hospital j
            - distance_indicators: Dict[str, Dict[str, int]] - Binary indicator for allowed distance
            - max_travel_distance: float - Maximum allowed travel distance
            - max_new_hospitals: int - Maximum number of new hospitals to open
    
    Returns:
        gurobipy.Model: The instantiated GurobiPy model
    """
    
    # Extract data
    households = data["households"]
    existing_hospitals = data["existing_hospitals"]
    candidate_hospitals = data["candidate_hospitals"]
    all_hospitals = data["all_hospitals"]
    population = data["population"]
    distance_indicators = data["distance_indicators"]
    max_new_hospitals = data["max_new_hospitals"]
    
    # Create model
    model = gp.Model("TimorLeste_Inefficient")
    
    # Variables: x_j = 1 if hospital j is opened, 0 otherwise
    x = {}
    for j in all_hospitals:
        x[j] = model.addVar(vtype=gp.GRB.BINARY, name=f"x_{j}")
    
    # Variables: y_{ij} = 1 if demand at household i is served by hospital j, 0 otherwise
    y = {}
    for i in households:
        for j in all_hospitals:
            y[i, j] = model.addVar(vtype=gp.GRB.BINARY, name=f"y_{i}_{j}")
    
    # Objective: Maximize the number of people served by healthcare facilities
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
    
    return model 