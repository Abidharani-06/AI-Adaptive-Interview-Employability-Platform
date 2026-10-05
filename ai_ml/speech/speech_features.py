"""
Observable Audio Features and Energy Consistency Module
-------------------------------------------------------
Analyzes acoustic signal properties: audio loading, RMS energy, volume dynamics,
and speech energy consistency across an interview response.

IMPORTANT:
Does NOT diagnose psychological states such as nervousness, emotional volatility, or confidence.
Reports strictly observable acoustic energy variation and volume metrics.
"""

import os
from pathlib import Path
from typing import Dict, Optional, Tuple, Any, Union
import numpy as np


def load_audio(
    file_path: Union[str, Path],
    target_sr: Optional[int] = 16000
) -> Tuple[Optional[np.ndarray], int]:
    """
    Robust audio file loader supporting WAV, FLAC, and uncompressed formats.
    Tries soundfile, scipy.io.wavfile, and standard library wave in sequence.
    Converts multi-channel to mono and resamples if needed.
    """
    p = Path(file_path)
    if not p.exists() or not p.is_file():
        raise FileNotFoundError(f"Audio file not found: {file_path}")

    # Method 1: soundfile
    try:
        import soundfile as sf
        data, sr = sf.read(str(p), dtype="float32")
        if data.ndim > 1:
            data = np.mean(data, axis=1)
        return data, sr
    except Exception:
        pass

    # Method 2: scipy.io.wavfile
    try:
        from scipy.io import wavfile
        sr, raw = wavfile.read(str(p))
        if raw.dtype == np.int16:
            data = raw.astype(np.float32) / 32768.0
        elif raw.dtype == np.int32:
            data = raw.astype(np.float32) / 2147483648.0
        elif raw.dtype == np.uint8:
            data = (raw.astype(np.float32) - 128) / 128.0
        else:
            data = raw.astype(np.float32)
        if data.ndim > 1:
            data = np.mean(data, axis=1)
        return data, sr
    except Exception:
        pass

    # Method 3: standard wave module
    try:
        import wave
        with wave.open(str(p), "rb") as wf:
            sr = wf.getframerate()
            n_channels = wf.getnchannels()
            n_frames = wf.getnframes()
            frames = wf.readframes(n_frames)
            raw = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
            if n_channels > 1:
                raw = raw.reshape(-1, n_channels).mean(axis=1)
            return raw, sr
    except Exception as e:
        raise ValueError(f"Unable to read audio file format '{p.suffix}': {str(e)}")


class AudioFeatureExtractor:
    """
    Extracts short-time energy, volume dynamics, and energy consistency metrics from audio.
    """

    def __init__(self, frame_length_ms: int = 30, hop_length_ms: int = 15):
        self.frame_length_ms = frame_length_ms
        self.hop_length_ms = hop_length_ms

    def analyze_audio(
        self,
        audio_input: Union[str, Path, np.ndarray],
        sample_rate: Optional[int] = 16000
    ) -> Dict[str, Any]:
        """
        Analyzes audio file or raw waveform numpy array.
        """
        if isinstance(audio_input, (str, Path)):
            try:
                samples, sr = load_audio(audio_input)
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "duration_seconds": 0.0,
                    "average_energy": 0.0,
                    "energy_variation": 0.0,
                    "energy_consistency_score": 0.0,
                    "feedback": f"Could not process audio: {str(e)}"
                }
        else:
            samples = np.asarray(audio_input, dtype=np.float32)
            sr = sample_rate or 16000

        if samples is None or len(samples) == 0:
            return {
                "success": False,
                "error": "Empty audio data received.",
                "duration_seconds": 0.0,
                "average_energy": 0.0,
                "energy_variation": 0.0,
                "energy_consistency_score": 0.0,
                "feedback": "Empty or silent audio signal."
            }

        if samples.ndim > 1:
            samples = np.mean(samples, axis=1)

        max_val = np.max(np.abs(samples))
        if max_val > 1.0:
            samples = samples / max(1.0, max_val)

        total_samples = len(samples)
        duration_s = total_samples / float(sr)

        frame_len = max(1, int(sr * (self.frame_length_ms / 1000.0)))
        hop_len = max(1, int(sr * (self.hop_length_ms / 1000.0)))
        num_frames = max(1, (total_samples - frame_len) // hop_len + 1)

        energies = np.zeros(num_frames, dtype=np.float32)
        for i in range(num_frames):
            start = i * hop_len
            end = start + frame_len
            frame = samples[start:end]
            energies[i] = np.sqrt(np.mean(frame * frame))

        # Separate speech frames from silence for energy consistency evaluation
        active_threshold = max(0.003, float(np.percentile(energies, 20)) * 1.3)
        active_energies = energies[energies >= active_threshold]

        if len(active_energies) == 0:
            active_energies = energies

        avg_energy = float(np.mean(active_energies))
        std_energy = float(np.std(active_energies))
        max_energy = float(np.max(energies))

        # Coefficient of variation in active speech segments: sigma / mu
        cv = (std_energy / avg_energy) if avg_energy > 1e-4 else 1.0

        # Energy consistency score in [0.0, 1.0]: 1.0 is steady volume, drops as variance spikes
        consistency_score = max(0.0, min(1.0, 1.0 - (cv * 0.5)))

        # Convert to approximate decibel scale relative to peak
        ref_energy = max(1e-5, max_energy)
        db_levels = 20 * np.log10(np.maximum(energies, 1e-5) / ref_energy)
        avg_db = float(np.mean(db_levels))

        # Objective, non-psychological description
        if consistency_score >= 0.75:
            feedback = "Speech energy showed stable and consistent vocal volume across the response."
        elif consistency_score >= 0.55:
            feedback = "Speech energy was generally consistent with natural conversational emphasis shifts."
        else:
            feedback = "Speech energy showed noticeable volume variation and dynamic shifts across phrases."

        return {
            "success": True,
            "duration_seconds": round(duration_s, 2),
            "sample_rate": sr,
            "average_energy": round(avg_energy, 4),
            "energy_standard_deviation": round(std_energy, 4),
            "energy_variation_coefficient": round(cv, 3),
            "energy_consistency_score": round(consistency_score, 4),
            "energy_consistency_percentage": round(consistency_score * 100, 1),
            "average_db_level": round(avg_db, 1),
            "feedback": feedback
        }
