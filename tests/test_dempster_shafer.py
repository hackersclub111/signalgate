import pytest
from src.dempster_shafer import DempsterShaferFusion

def test_normalization():
    raw = {"Victim": 2.0, "Noise": 2.0, "Hazard": 0.0, "Theta": 0.0}
    norm = DempsterShaferFusion.normalize_mass(raw)
    assert norm["Victim"] == 0.5
    assert norm["Noise"] == 0.5
    assert sum(norm.values()) == 1.0

def test_agreement_reinforcement():
    # When two sensors agree on Victim, belief should strengthen
    m1 = {"Victim": 0.70, "Noise": 0.10, "Hazard": 0.05, "Theta": 0.15}
    m2 = {"Victim": 0.75, "Noise": 0.05, "Hazard": 0.05, "Theta": 0.15}
    
    combined, k = DempsterShaferFusion.combine_pair(m1, m2)
    # Combined victim belief must be strictly higher than individual inputs
    assert combined["Victim"] > 0.75
    # Conflict should be low
    assert k < 0.25

def test_high_conflict_detection():
    # Sensor 1 says Victim, Sensor 2 says Noise
    m1 = {"Victim": 0.90, "Noise": 0.05, "Hazard": 0.0, "Theta": 0.05}
    m2 = {"Victim": 0.05, "Noise": 0.90, "Hazard": 0.0, "Theta": 0.05}
    
    combined, k = DempsterShaferFusion.combine_pair(m1, m2)
    # Conflict K should be high
    assert k >= 0.75

def test_total_ignorance_neutral_element():
    # Combining with Theta (total ignorance) must preserve the original belief
    m1 = {"Victim": 0.80, "Noise": 0.10, "Hazard": 0.05, "Theta": 0.05}
    theta = {"Victim": 0.0, "Noise": 0.0, "Hazard": 0.0, "Theta": 1.0}
    
    combined, k = DempsterShaferFusion.combine_pair(m1, theta)
    assert k == 0.0
    assert abs(combined["Victim"] - m1["Victim"]) < 1e-3
