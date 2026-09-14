"""
ResQ-Mesh Crisis Speech & Keyword Spotting Engine
Grounded in Adaption Labs synthetic crisis dataset across 5 high-risk dialects:
- Tagalog (tl)
- Haitian Creole (ht)
- Ukrainian (uk)
- Turkish (tr)
- Spanish (es)
"""

import os
import json
from typing import Dict, Optional, Tuple

class CrisisNLPEngine:
    def __init__(self, lexicon_path: Optional[str] = None):
        if lexicon_path is None:
            lexicon_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "data", "synthetic_crisis_lexicon", "crisis_lexicon_5_dialects.json"
            )
        self.lexicon_path = lexicon_path
        self.lexicon = self._load_lexicon()

    def _load_lexicon(self) -> Dict:
        if not os.path.exists(self.lexicon_path):
            raise FileNotFoundError(f"Adaption Labs dataset not found at {self.lexicon_path}. Run generate_adaption_lexicon.py first.")
        with open(self.lexicon_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def analyze_text(self, text: str) -> Dict[str, float]:
        """
        Analyze incoming speech transcription or typed message against the Adaption Labs crisis lexicon.
        Returns Dempster-Shafer mass assignment:
        { "Victim": m, "Noise": m, "Hazard": m, "Theta": m, "detected_dialect": str, "urgency": str }
        """
        text_lower = text.lower().strip()
        best_match = None
        highest_score = 0.0
        detected_lang = "unknown"

        for lang_code, lang_data in self.lexicon.get("dialects", {}).items():
            for item in lang_data.get("keywords", []):
                phrase = item["phrase"].lower()
                # Check direct substring or word overlap
                words = set(phrase.replace("!", "").replace(",", "").split())
                input_words = set(text_lower.replace("!", "").replace(",", "").split())
                overlap = len(words.intersection(input_words))
                score = overlap / max(1, len(words))

                if phrase in text_lower:
                    score = 1.0

                if score > highest_score and score >= 0.35:
                    highest_score = score
                    best_match = item
                    detected_lang = lang_code

        if best_match and highest_score >= 0.70:
            urgency = best_match["urgency"]
            m_victim = float(best_match["mass_victim"])
            m_noise = 0.04
            m_hazard = 0.04
            m_theta = max(0.02, 1.0 - (m_victim + m_noise + m_hazard))
        elif best_match and highest_score >= 0.35:
            # Partial match / high epistemic uncertainty
            urgency = best_match["urgency"]
            m_victim = float(best_match["mass_victim"]) * 0.65
            m_noise = 0.15
            m_hazard = 0.05
            m_theta = max(0.15, 1.0 - (m_victim + m_noise + m_hazard))
        else:
            # No crisis keyword found -> likely ambient banter, radio static, or benign chatter
            urgency = "P3"
            m_victim = 0.05
            m_noise = 0.80
            m_hazard = 0.05
            m_theta = 0.10

        return {
            "Victim": round(m_victim, 4),
            "Noise": round(m_noise, 4),
            "Hazard": round(m_hazard, 4),
            "Theta": round(m_theta, 4),
            "detected_dialect": detected_lang,
            "urgency": urgency,
            "match_confidence": round(highest_score, 2)
        }
