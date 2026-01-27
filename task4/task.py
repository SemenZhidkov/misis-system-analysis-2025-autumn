import json
import ast


def membership_value(points, x):
    n = len(points)
    if x <= points[0][0]:
        return points[0][1]
    if x >= points[n - 1][0]:
        return points[n - 1][1]
    
    for i in range(n - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        if x1 <= x <= x2:
            if x2 == x1:
                return y1
            return y1 + (y2 - y1) * (x - x1) / (x2 - x1)
    return 0.0


def fuzzify(temperature_terms, temperature_value):
    memberships = {}
    for term in temperature_terms:
        term_id = term["id"]
        points = term["points"]
        memberships[term_id] = membership_value(points, temperature_value)
    return memberships


def normalize_term(term, available_terms):
    if term in available_terms:
        return term
    
    term_mappings = {
        'нормально': 'комфортно',
        'умеренно': 'умеренный',
        'слабо': 'слабый',
        'интенсивно': 'интенсивный'
    }
    
    if term in term_mappings and term_mappings[term] in available_terms:
        return term_mappings[term]
    
    term_lower = term.lower()
    for available in available_terms:
        if available.lower().startswith(term_lower[:4]) or term_lower[:4] in available.lower():
            return available
    
    return term


def apply_rules(rules, temperature_memberships, control_term_ids):
    activated = {}
    
    for rule in rules:
        temp_term, control_term = rule[0], rule[1]
        
        normalized_temp = normalize_term(temp_term, temperature_memberships.keys())
        normalized_control = normalize_term(control_term, control_term_ids)
        
        temp_membership = temperature_memberships.get(normalized_temp, 0.0)
        
        if temp_membership > 0 and normalized_control in control_term_ids:
            if normalized_control not in activated:
                activated[normalized_control] = temp_membership
            else:
                activated[normalized_control] = max(activated[normalized_control], temp_membership)
    
    return activated


def defuzzify_centroid(control_terms, activations, step=0.1):
    if not control_terms:
        return 0.0
    
    x_min = min(term["points"][0][0] for term in control_terms)
    x_max = max(term["points"][-1][0] for term in control_terms)
    
    x_values = []
    y_values = []
    
    x = x_min
    while x <= x_max:
        aggregated = 0.0
        for term in control_terms:
            term_id = term["id"]
            if term_id in activations:
                membership = membership_value(term["points"], x)
                aggregated = max(aggregated, min(membership, activations[term_id]))
        
        x_values.append(x)
        y_values.append(aggregated)
        x += step
    
    numerator = sum(x_values[i] * y_values[i] for i in range(len(x_values)))
    denominator = sum(y_values)
    
    if denominator == 0:
        return 0.0
    
    return numerator / denominator


def main(temperature_json, control_json, rules_json, temperature_value):
    try:
        temp_data = json.loads(temperature_json)
    except (json.JSONDecodeError, ValueError):
        temp_data = ast.literal_eval(temperature_json)
    
    try:
        control_data = json.loads(control_json)
    except (json.JSONDecodeError, ValueError):
        control_data = ast.literal_eval(control_json)
    
    try:
        rules = json.loads(rules_json)
    except (json.JSONDecodeError, ValueError):
        rules = ast.literal_eval(rules_json)
    
    temperature_terms = temp_data.get("температура", [])
    control_terms = control_data.get("температура", [])
    
    control_term_ids = [term["id"] for term in control_terms]
    
    temperature_memberships = fuzzify(temperature_terms, temperature_value)
    activations = apply_rules(rules, temperature_memberships, control_term_ids)
    result = defuzzify_centroid(control_terms, activations)
    
    return result
