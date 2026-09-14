import pytest
from src.mesh_simulator import MeshNetworkSimulator
from src.chaos_injector import ChaosFaultInjector

def test_mesh_packet_transmission():
    sim = MeshNetworkSimulator(packet_loss_rate=0.0)
    m1 = {"Victim": 0.85, "Noise": 0.05, "Hazard": 0.05, "Theta": 0.05}
    decision = sim.process_incident("NODE_01", [m1])
    
    assert decision["state"] == "DISPATCH"
    assert decision["mesh_telemetry"]["delivered"] is True
    assert decision["mesh_telemetry"]["hops"] >= 1
    assert decision["mesh_telemetry"]["internet_status"] == "OFFLINE"

def test_corroboration_escalation():
    sim = MeshNetworkSimulator(packet_loss_rate=0.0)
    # Ambiguous first signal -> HOLD
    m1 = {"Victim": 0.55, "Noise": 0.10, "Hazard": 0.05, "Theta": 0.30}
    decision = sim.process_incident("NODE_01", [m1])
    assert decision["state"] == "HOLD_AND_CORROBORATE"
    dec_id = decision["decision_id"]
    assert dec_id in sim.active_holds

    # Node 2 sends strong corroboration
    m2 = {"Victim": 0.85, "Noise": 0.05, "Hazard": 0.05, "Theta": 0.05}
    escalated = sim.corroborate_incident(dec_id, "NODE_02", m2)
    assert escalated is not None
    assert escalated["state"] == "DISPATCH"
    assert dec_id not in sim.active_holds

def test_chaos_mode_fault_injection():
    injector = ChaosFaultInjector(seed=42)
    report = injector.run_chaos_evaluation(num_scenarios=50)
    
    assert report["total_scenarios_tested"] == 50
    # In our 25 conflict scenarios, the system must hold without false dispatches
    assert report["metrics"]["false_dispatches_on_conflict"] == 0
    assert report["metrics"]["false_dispatch_rate_pct"] == 0.0
    assert report["metrics"]["conflict_cases_safely_held"] == 25
    assert report["metrics"]["corroboration_recovery_rate_pct"] >= 90.0
