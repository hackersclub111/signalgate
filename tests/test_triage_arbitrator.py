import pytest
from src.triage_arbitrator import TriageArbitrator

def test_dispatch_on_conclusive_evidence():
    fused_mass = {"Victim": 0.88, "Noise": 0.05, "Hazard": 0.02, "Theta": 0.05}
    decision = TriageArbitrator.arbitrate("NODE_01", fused_mass, conflict_k=0.10)
    
    assert decision["state"] == "DISPATCH"
    assert decision["priority"] == "P0_IMMEDIATE"
    assert TriageArbitrator.verify_provenance(decision) is True

def test_refusal_to_dispatch_on_high_conflict():
    fused_mass = {"Victim": 0.50, "Noise": 0.45, "Hazard": 0.0, "Theta": 0.05}
    decision = TriageArbitrator.arbitrate("NODE_01", fused_mass, conflict_k=0.65)
    
    assert decision["state"] == "HOLD_AND_CORROBORATE"
    assert "High inter-sensor conflict" in decision["reason"]
    assert TriageArbitrator.verify_provenance(decision) is True

def test_refusal_to_dispatch_on_high_ignorance():
    fused_mass = {"Victim": 0.45, "Noise": 0.10, "Hazard": 0.05, "Theta": 0.40}
    decision = TriageArbitrator.arbitrate("NODE_01", fused_mass, conflict_k=0.15)
    
    assert decision["state"] == "HOLD_AND_CORROBORATE"
    assert "High epistemic ignorance" in decision["reason"]

def test_ignore_on_environmental_noise():
    fused_mass = {"Victim": 0.02, "Noise": 0.88, "Hazard": 0.02, "Theta": 0.08}
    decision = TriageArbitrator.arbitrate("NODE_01", fused_mass, conflict_k=0.05)
    
    assert decision["state"] == "IGNORE"
    assert decision["priority"] == "P3_BENIGN"

def test_tamper_detection():
    fused_mass = {"Victim": 0.88, "Noise": 0.05, "Hazard": 0.02, "Theta": 0.05}
    decision = TriageArbitrator.arbitrate("NODE_01", fused_mass, conflict_k=0.10)
    
    # Tamper with decision priority
    decision["priority"] = "TAMPERED_PRIORITY"
    assert TriageArbitrator.verify_provenance(decision) is False
