import pytest
import numpy as np
from src.dsp_sensor import AcousticDSPSensor
from src.crisis_nlp import CrisisNLPEngine

def test_dsp_acoustic_tapping_detection():
    sensor = AcousticDSPSensor()
    # Synthesize Morse SOS tapping
    tone = AcousticDSPSensor.synthesize_test_tone(pattern="sos", duration_s=0.5)
    res = sensor.analyze_frame(tone)
    
    assert res["Victim"] >= 0.50
    assert res["rms"] > 0.05
    assert 100.0 <= res["dominant_freq_hz"] <= 1800.0

def test_dsp_rain_noise_rejection():
    sensor = AcousticDSPSensor()
    rain = AcousticDSPSensor.synthesize_test_tone(pattern="rain_noise", duration_s=0.5)
    res = sensor.analyze_frame(rain)
    
    assert res["Noise"] >= 0.70
    assert res["Victim"] < 0.10

def test_adaption_labs_multilingual_nlp():
    nlp = CrisisNLPEngine()
    
    # 1. Tagalog
    res_tl = nlp.analyze_text("Tulong! Natabunan kami sa ilalim")
    assert res_tl["detected_dialect"] == "tl"
    assert res_tl["urgency"] == "P0"
    assert res_tl["Victim"] >= 0.80

    # 2. Ukrainian
    res_uk = nlp.analyze_text("Допоможіть! Ми під завалами")
    assert res_uk["detected_dialect"] == "uk"
    assert res_uk["urgency"] == "P0"
    assert res_uk["Victim"] >= 0.80

    # 3. Haitian Creole
    res_ht = nlp.analyze_text("Tanpri ede m! M anba dekonb yo")
    assert res_ht["detected_dialect"] == "ht"
    assert res_ht["urgency"] == "P0"
    assert res_ht["Victim"] >= 0.80

    # 4. Spanish
    res_es = nlp.analyze_text("¡Ayuda! Estamos atrapados bajo los escombros")
    assert res_es["detected_dialect"] == "es"
    assert res_es["urgency"] == "P0"
    assert res_es["Victim"] >= 0.80

    # 5. Turkish
    res_tr = nlp.analyze_text("İmdat! Enkaz altındayız, nefes alamıyorum")
    assert res_tr["detected_dialect"] == "tr"
    assert res_tr["urgency"] == "P0"
    assert res_tr["Victim"] >= 0.80

    # 6. Benign environmental comment
    res_benign = nlp.analyze_text("Just casual conversation about the sunny weather")
    assert res_benign["urgency"] == "P3"
    assert res_benign["Noise"] >= 0.70
