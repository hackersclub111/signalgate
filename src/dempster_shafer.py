"""
ResQ-Mesh Mathematical Evidential Fusion Engine
Implements Dempster-Shafer Theory of Evidence (DST) over Frame of Discernment:
Omega = {"Victim", "Noise", "Hazard"}

Calculates:
- Conflict Metric (K)
- Epistemic Uncertainty / Ignorance mass m(Theta)
- Joint Belief and Plausibility bounds
"""

from typing import Dict, List, Tuple

FOCAL_SETS = ["Victim", "Noise", "Hazard", "Theta"]

class DempsterShaferFusion:
    @staticmethod
    def normalize_mass(m: Dict[str, float]) -> Dict[str, float]:
        """Ensure non-negative mass values sum to 1.0."""
        cleaned = {k: max(0.0, float(m.get(k, 0.0))) for k in FOCAL_SETS}
        total = sum(cleaned.values())
        if total == 0.0:
            return {"Victim": 0.0, "Noise": 0.0, "Hazard": 0.0, "Theta": 1.0}
        return {k: round(v / total, 6) for k, v in cleaned.items()}

    @classmethod
    def combine_pair(cls, m1: Dict[str, float], m2: Dict[str, float]) -> Tuple[Dict[str, float], float]:
        """
        Combine two mass functions m1 and m2 using Dempster's rule of combination.
        Returns:
            (combined_mass_dict, conflict_metric_K)
        """
        m1 = cls.normalize_mass(m1)
        m2 = cls.normalize_mass(m2)

        # In our simplified frame Omega = {V, N, H}:
        # Intersection table:
        # V & V = V
        # N & N = N
        # H & H = H
        # Any & Theta = Any
        # Theta & Theta = Theta
        # V & N = empty (Conflict)
        # V & H = empty (Conflict)
        # N & H = empty (Conflict)

        # 1. Compute conflict K (sum of products yielding empty set)
        k = (
            m1["Victim"] * (m2["Noise"] + m2["Hazard"]) +
            m1["Noise"]  * (m2["Victim"] + m2["Hazard"]) +
            m1["Hazard"] * (m2["Victim"] + m2["Noise"])
        )
        k = min(0.999999, max(0.0, k))

        normalization = 1.0 - k
        if normalization <= 1e-6:
            # Extreme conflict: total contradiction (Zadeh's paradox boundary)
            # Default to total epistemic ignorance
            return {"Victim": 0.0, "Noise": 0.0, "Hazard": 0.0, "Theta": 1.0}, 1.0

        # 2. Combine non-empty intersections
        v_num = (
            m1["Victim"] * m2["Victim"] +
            m1["Victim"] * m2["Theta"] +
            m1["Theta"]  * m2["Victim"]
        )
        n_num = (
            m1["Noise"] * m2["Noise"] +
            m1["Noise"] * m2["Theta"] +
            m1["Theta"] * m2["Noise"]
        )
        h_num = (
            m1["Hazard"] * m2["Hazard"] +
            m1["Hazard"] * m2["Theta"] +
            m1["Theta"]  * m2["Hazard"]
        )
        theta_num = m1["Theta"] * m2["Theta"]

        combined = {
            "Victim": round(v_num / normalization, 4),
            "Noise": round(n_num / normalization, 4),
            "Hazard": round(h_num / normalization, 4),
            "Theta": round(theta_num / normalization, 4)
        }
        return combined, round(k, 4)

    @classmethod
    def combine_multiple(cls, mass_list: List[Dict[str, float]]) -> Tuple[Dict[str, float], float]:
        """
        Sequentially combine a list of sensor mass functions.
        Returns accumulated combined mass and maximum pairwise conflict encountered.
        """
        if not mass_list:
            return {"Victim": 0.0, "Noise": 0.0, "Hazard": 0.0, "Theta": 1.0}, 0.0
        if len(mass_list) == 1:
            return cls.normalize_mass(mass_list[0]), 0.0

        accumulated = mass_list[0]
        max_conflict = 0.0

        for current in mass_list[1:]:
            accumulated, k = cls.combine_pair(accumulated, current)
            max_conflict = max(max_conflict, k)

        return accumulated, max_conflict
