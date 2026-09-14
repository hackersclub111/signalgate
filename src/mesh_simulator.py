"""
ResQ-Mesh Distributed P2P Mesh Relay Simulator
Simulates offline mesh networking across 3 field nodes and a Command Post.
Features:
- Multi-hop packet routing
- Configurable packet loss & transmission jitter
- Multi-node spatial corroboration
"""

import random
import time
from typing import Dict, List, Any, Optional, Tuple
from .dempster_shafer import DempsterShaferFusion
from .triage_arbitrator import TriageArbitrator

class MeshNode:
    def __init__(self, node_id: str, role: str, lat: float, lon: float):
        self.node_id = node_id
        self.role = role
        self.lat = lat
        self.lon = lon
        self.packet_log: List[Dict[str, Any]] = []

    def log_packet(self, packet: Dict[str, Any]) -> None:
        self.packet_log.append(packet)

class MeshNetworkSimulator:
    def __init__(self, packet_loss_rate: float = 0.0, simulated_hop_latency_ms: float = 2.0):
        self.loss_rate = packet_loss_rate
        self.hop_latency_ms = simulated_hop_latency_ms
        self.nodes = {
            "NODE_01": MeshNode("NODE_01", "Acoustic DSP / Mic Node", 14.5995, 120.9842),
            "NODE_02": MeshNode("NODE_02", "Seismic / Accelerometer Node", 14.6010, 120.9855),
            "NODE_03": MeshNode("NODE_03", "Crisis Speech / RF Relay", 14.5980, 120.9830),
            "COMMAND": MeshNode("COMMAND", "Incident Command Base Post", 14.6050, 120.9900)
        }
        self.active_holds: Dict[str, Dict[str, Any]] = {}
        self.dispatched_events: List[Dict[str, Any]] = []

    def transmit_packet(self, source_id: str, dest_id: str, payload: Dict[str, Any]) -> Tuple[bool, int, float]:
        """
        Simulate packet hop from source to destination.
        Returns (delivered_bool, hop_count, total_latency_ms).
        """
        # Determine routing path
        # In a 3-node topology to Command:
        # NODE_01 -> NODE_02 -> NODE_03 -> COMMAND (up to 3 hops)
        hops = 2 if source_id in ["NODE_01", "NODE_02"] else 1
        
        # Check packet loss
        if random.random() < self.loss_rate:
            # Packet dropped due to mesh RF collision or structural shadowing
            return False, hops, hops * self.hop_latency_ms

        total_latency = hops * self.hop_latency_ms + random.uniform(0.1, 0.8)
        dest_node = self.nodes.get(dest_id)
        if dest_node:
            dest_node.log_packet(payload)
        return True, hops, round(total_latency, 2)

    def process_incident(
        self,
        origin_node_id: str,
        initial_masses: List[Dict[str, float]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a single incident from a sensor node through the fusion and arbitration pipeline.
        If held for corroboration, registers into active_holds.
        """
        fused_mass, conflict_k = DempsterShaferFusion.combine_multiple(initial_masses)
        decision = TriageArbitrator.arbitrate(origin_node_id, fused_mass, conflict_k, metadata)

        delivered, hops, latency = self.transmit_packet(origin_node_id, "COMMAND", decision)
        decision["mesh_telemetry"] = {
            "delivered": delivered,
            "hops": hops,
            "simulated_latency_ms": latency,
            "internet_status": "OFFLINE",
            "transport": "Simulated LoRa / P2P Mesh (868MHz)"
        }

        if decision["state"] == "HOLD_AND_CORROBORATE":
            self.active_holds[decision["decision_id"]] = decision
        elif decision["state"] == "DISPATCH":
            self.dispatched_events.append(decision)

        return decision

    def corroborate_incident(
        self,
        decision_id: str,
        corroborating_node_id: str,
        new_mass: Dict[str, float]
    ) -> Optional[Dict[str, Any]]:
        """
        Corroborate a pending held incident with new independent evidence from another node.
        """
        if decision_id not in self.active_holds:
            return None

        original = self.active_holds[decision_id]
        prior_mass = original["fused_mass"]
        
        # Combine prior mass with new corroborating mass
        new_fused_mass, new_conflict_k = DempsterShaferFusion.combine_pair(prior_mass, new_mass)
        new_decision = TriageArbitrator.arbitrate(
            corroborating_node_id,
            new_fused_mass,
            new_conflict_k,
            metadata={"corroborated_from": decision_id, "nodes_involved": [original["node_id"], corroborating_node_id]}
        )

        delivered, hops, latency = self.transmit_packet(corroborating_node_id, "COMMAND", new_decision)
        new_decision["mesh_telemetry"] = {
            "delivered": delivered,
            "hops": hops,
            "simulated_latency_ms": latency,
            "internet_status": "OFFLINE",
            "transport": "Simulated LoRa / P2P Mesh (868MHz)"
        }

        if new_decision["state"] == "DISPATCH":
            del self.active_holds[decision_id]
            self.dispatched_events.append(new_decision)

        return new_decision
