"""
SignalGate Triage Decision Arbitrator & State Machine
The core decision architecture:
Refuses to escalate uncorroborated, conflicting, or ignorant signals.
Generates HMAC-SHA256 cryptographic receipts for verifiable audit trails.
"""

import hmac
import hashlib
import json
import time
from typing import Dict, Any, Tuple, Optional
from datetime import datetime, timezone

SECRET_KEY = b"signalgate-hyperbloom-audit-secret-2026"

class TriageArbitrator:
    # Thresholds
    DISPATCH_VICTIM_THRESHOLD = 0.72
    CONFLICT_HOLD_THRESHOLD = 0.45
    IGNORANCE_HOLD_THRESHOLD = 0.35
    NOISE_IGNORE_THRESHOLD = 0.70

    @classmethod
    def arbitrate(
        cls,
        node_id: str,
        fused_mass: Dict[str, float],
        conflict_k: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate fused evidence and decide triage action:
        - DISPATCH (P0 or P1)
        - HOLD_AND_CORROBORATE
        - IGNORE
        """
        m_victim = fused_mass.get("Victim", 0.0)
        m_noise = fused_mass.get("Noise", 0.0)
        m_hazard = fused_mass.get("Hazard", 0.0)
        m_theta = fused_mass.get("Theta", 0.0)

        timestamp = datetime.now(timezone.utc).isoformat()
        decision_id = f"TRG-{node_id}-{int(time.time() * 1000)}"

        # 1. Check for high conflict or high ignorance (Refuse to dispatch!)
        if conflict_k >= cls.CONFLICT_HOLD_THRESHOLD:
            state = "HOLD_AND_CORROBORATE"
            priority = "P2_HOLD"
            action_code = "REQUEST_MULTI_NODE_CORROBORATION"
            reason = f"High inter-sensor conflict (K={conflict_k:.2f} >= {cls.CONFLICT_HOLD_THRESHOLD}). Contradictory evidence detected; refusing dispatch."
        elif m_theta >= cls.IGNORANCE_HOLD_THRESHOLD and m_victim < 0.85:
            state = "HOLD_AND_CORROBORATE"
            priority = "P2_HOLD"
            action_code = "PROBE_ADDITIONAL_SENSORS"
            reason = f"High epistemic ignorance (m(Theta)={m_theta:.2f} >= {cls.IGNORANCE_HOLD_THRESHOLD}). Signal ambiguous; awaiting sensor accumulation."
        elif m_victim >= cls.DISPATCH_VICTIM_THRESHOLD:
            state = "DISPATCH"
            priority = "P0_IMMEDIATE" if (m_victim >= 0.85 or m_hazard >= 0.20) else "P1_URGENT"
            action_code = "DISPATCH_EXTRACTION_TEAM"
            reason = f"Conclusive victim evidence (m(Victim)={m_victim:.2f}, conflict K={conflict_k:.2f}). Corroborated consensus satisfied."
        elif m_noise >= cls.NOISE_IGNORE_THRESHOLD:
            state = "IGNORE"
            priority = "P3_BENIGN"
            action_code = "SUPPRESS_ALERT"
            reason = f"Conclusive environmental noise (m(Noise)={m_noise:.2f}). No casualty indicator."
        else:
            state = "HOLD_AND_CORROBORATE"
            priority = "P2_MONITOR"
            action_code = "CONTINUE_PASSIVE_LISTENING"
            reason = f"Sub-threshold evidence (m(V)={m_victim:.2f}, m(N)={m_noise:.2f}). Monitoring."

        record = {
            "decision_id": decision_id,
            "timestamp": timestamp,
            "node_id": node_id,
            "state": state,
            "priority": priority,
            "action_code": action_code,
            "reason": reason,
            "fused_mass": fused_mass,
            "conflict_k": conflict_k,
            "metadata": metadata or {}
        }

        # Generate HMAC-SHA256 signature
        payload_bytes = json.dumps(record, sort_keys=True).encode("utf-8")
        signature = hmac.new(SECRET_KEY, payload_bytes, hashlib.sha256).hexdigest()
        record["provenance_signature"] = signature
        return record

    @classmethod
    def verify_provenance(cls, record: Dict[str, Any]) -> bool:
        """Verify HMAC-SHA256 signature to guarantee tampering immunity."""
        claimed_sig = record.get("provenance_signature")
        if not claimed_sig:
            return False
        clean_record = {k: v for k, v in record.items() if k != "provenance_signature"}
        payload_bytes = json.dumps(clean_record, sort_keys=True).encode("utf-8")
        expected_sig = hmac.new(SECRET_KEY, payload_bytes, hashlib.sha256).hexdigest()
        return hmac.compare_digest(claimed_sig, expected_sig)
