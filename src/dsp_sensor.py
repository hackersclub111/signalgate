"""
ResQ-Mesh Bare-Metal Acoustic DSP Engine (CodeCrafters Ethos)
Pure NumPy sliding window and FFT energy/cadence analyzer.
Zero heavy frameworks (no Librosa, no PyAudio, no SciPy).
8GB-RAM Safe & Sub-5ms CPU execution.
"""

import numpy as np
from typing import Dict, Tuple, List

class AcousticDSPSensor:
    def __init__(self, sample_rate_hz: int = 16000, window_size_ms: int = 250, hop_size_ms: int = 50):
        self.sample_rate = sample_rate_hz
        self.window_size = int(sample_rate_hz * (window_size_ms / 1000.0))  # 4000 samples
        self.hop_size = int(sample_rate_hz * (hop_size_ms / 1000.0))        # 800 samples
        self.buffer = np.zeros(self.window_size, dtype=np.float32)
        # Precompute Hann window to avoid per-frame allocation
        self.hann_window = 0.5 * (1.0 - np.cos(2.0 * np.pi * np.arange(self.window_size) / (self.window_size - 1)))

    def push_samples(self, new_samples: np.ndarray) -> None:
        """Push streaming audio into the circular sliding buffer."""
        n = len(new_samples)
        if n >= self.window_size:
            self.buffer = new_samples[-self.window_size:].astype(np.float32)
        else:
            self.buffer = np.roll(self.buffer, -n)
            self.buffer[-n:] = new_samples.astype(np.float32)

    def compute_energy_and_dominant_freq(self) -> Tuple[float, float]:
        """Compute RMS energy and dominant frequency using sliding FFT across the window."""
        # RMS energy
        rms = float(np.sqrt(np.mean(self.buffer ** 2) + 1e-9))
        
        # Apply precomputed Hann window
        windowed = self.buffer * self.hann_window
        
        # Compute rfft across full window (4000 samples -> 2001 frequency bins, 4Hz resolution)
        fft_out = np.abs(np.fft.rfft(windowed))
        freqs = np.fft.rfftfreq(len(windowed), d=1.0 / self.sample_rate)
        
        # Dominant frequency (exclude DC component at index 0)
        peak_idx = int(np.argmax(fft_out[1:])) + 1 if len(fft_out) > 1 else 0
        peak_freq = float(freqs[peak_idx])
        return rms, peak_freq

    def analyze_frame(self, audio_data: np.ndarray = None) -> Dict[str, float]:
        """
        Analyze current frame and produce Dempster-Shafer mass assignment:
        { "Victim": m, "Noise": m, "Hazard": m, "Theta": m }
        """
        if audio_data is not None:
            self.push_samples(audio_data)

        rms, peak_freq = self.compute_energy_and_dominant_freq()

        # Structural tapping distress characteristics:
        # Tapping on concrete/pipes typically concentrates between 100 Hz and 1800 Hz.
        is_impulsive = rms > 0.06
        is_tapping_band = 100.0 <= peak_freq <= 1800.0

        if is_impulsive and is_tapping_band:
            # High belief of acoustic distress tapping
            m_victim = min(0.92, 0.50 + (rms * 1.8))
            m_noise = 0.04
            m_hazard = 0.04
            m_theta = max(0.04, 1.0 - (m_victim + m_noise + m_hazard))
        elif is_impulsive and not is_tapping_band:
            # High energy but out-of-band (e.g., machinery roar or electrical hum)
            m_victim = 0.10
            m_hazard = 0.40
            m_noise = 0.40
            m_theta = 0.10
        else:
            # Low energy background noise
            m_victim = 0.02
            m_noise = 0.85
            m_hazard = 0.03
            m_theta = 0.10

        return {
            "Victim": round(m_victim, 4),
            "Noise": round(m_noise, 4),
            "Hazard": round(m_hazard, 4),
            "Theta": round(m_theta, 4),
            "rms": round(rms, 4),
            "dominant_freq_hz": round(peak_freq, 1)
        }

    @staticmethod
    def synthesize_test_tone(pattern: str = "sos", sample_rate: int = 16000, duration_s: float = 0.25) -> np.ndarray:
        """Helper to generate synthetic acoustic test patterns for benchmarks and chaos mode."""
        n_samples = int(sample_rate * duration_s)
        t = np.linspace(0, duration_s, n_samples, endpoint=False)
        audio = np.zeros(n_samples, dtype=np.float32)

        if pattern == "sos":
            # 3 rhythmic bursts (Morse S: . . .)
            burst_len = int(sample_rate * 0.04) # 40ms burst
            for frac in [0.15, 0.45, 0.75]:
                idx = int(n_samples * frac)
                end_idx = min(n_samples, idx + burst_len)
                actual_len = end_idx - idx
                audio[idx:end_idx] = 0.75 * np.sin(2 * np.pi * 500.0 * t[:actual_len])
            return audio
        elif pattern == "rain_noise":
            # Broadband low-amplitude Gaussian noise
            return (0.02 * np.random.randn(n_samples)).astype(np.float32)
        elif pattern == "machinery":
            # 60Hz hum + harmonics
            return (0.4 * np.sin(2 * np.pi * 60 * t) + 0.2 * np.sin(2 * np.pi * 120 * t)).astype(np.float32)
        elif pattern == "crack":
            # Sudden high frequency collapse snap
            audio = (0.01 * np.random.randn(n_samples)).astype(np.float32)
            snap_idx = int(n_samples * 0.5)
            end_snap = min(n_samples, snap_idx + 200)
            audio[snap_idx:end_snap] += (0.9 * np.sin(2 * np.pi * 2200 * t[:end_snap - snap_idx])).astype(np.float32)
            return audio
        return audio
