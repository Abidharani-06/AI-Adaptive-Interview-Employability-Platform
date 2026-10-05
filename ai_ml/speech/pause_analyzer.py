"""
Observable Pause and Voice Activity Analysis Module
---------------------------------------------------
Analyzes silent intervals and vocal pauses in speech audio signals.
Measures pause count, average pause duration, longest pause, and speech-active ratio.

IMPORTANT:
Does NOT diagnose psychological states, hesitation as anxiety, or nervousness.
Measures strictly observable acoustic silence intervals.
"""

import math
from typing import Dict, List, Optional, Tuple, Any
import numpy as np


class PauseAnalyzer:
    """
    Analyzes observable pause characteristics and voice activity from acoustic signals.
    """

    def __init__(
        self,
        min_pause_duration_s: float = 0.30,
        frame_duration_ms: int = 25,
        hop_duration_ms: int = 10,
        silence_threshold_ratio: float = 0.18
    ):
        """
        Parameters:
        - min_pause_duration_s: Minimum silence duration (in seconds) to be counted as a pause episode (default: 300ms).
        - frame_duration_ms: Short-time energy frame window in milliseconds.
        - hop_duration_ms: Frame step hop size in milliseconds.
        - silence_threshold_ratio: Energy threshold relative to average audio energy.
        """
        self.min_pause_duration_s = min_pause_duration_s
        self.frame_duration_ms = frame_duration_ms
        self.hop_duration_ms = hop_duration_ms
        self.silence_threshold_ratio = silence_threshold_ratio

    def analyze_signal(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, Any]:
        """
        Processes audio waveform array and extracts pause metrics.

        Parameters:
        - audio_data: 1D numpy array of audio samples (float32 or int16).
        - sample_rate: Audio sampling frequency in Hz.
        """
        if audio_data is None or len(audio_data) == 0 or sample_rate <= 0:
            return {
                "total_duration_seconds": 0.0,
                "pause_count": 0,
                "total_pause_duration": 0.0,
                "average_pause_duration": 0.0,
                "longest_pause": 0.0,
                "speech_active_duration": 0.0,
                "speech_active_ratio": 0.0,
                "pause_rate_per_minute": 0.0,
                "feedback": "No audio signal data available for pause analysis."
            }

        # Convert to 1D float32 normalized [-1.0, 1.0]
        samples = np.asarray(audio_data, dtype=np.float32)
        if samples.ndim > 1:
            samples = np.mean(samples, axis=1)

        max_val = np.max(np.abs(samples))
        if max_val > 1.0:
            samples = samples / 32768.0

        total_samples = len(samples)
        total_duration = total_samples / float(sample_rate)

        if total_duration < 0.10:
            return {
                "total_duration_seconds": round(total_duration, 2),
                "pause_count": 0,
                "total_pause_duration": 0.0,
                "average_pause_duration": 0.0,
                "longest_pause": 0.0,
                "speech_active_duration": round(total_duration, 2),
                "speech_active_ratio": 1.0,
                "pause_rate_per_minute": 0.0,
                "feedback": "Audio duration is too short to evaluate conversational pause patterns."
            }

        frame_len = max(1, int(sample_rate * (self.frame_duration_ms / 1000.0)))
        hop_len = max(1, int(sample_rate * (self.hop_duration_ms / 1000.0)))

        # Compute Short-Time RMS energy
        num_frames = max(1, (total_samples - frame_len) // hop_len + 1)
        energies = np.zeros(num_frames, dtype=np.float32)

        for i in range(num_frames):
            start = i * hop_len
            end = start + frame_len
            frame = samples[start:end]
            energies[i] = np.sqrt(np.mean(frame * frame))

        mean_energy = float(np.mean(energies))
        max_energy = float(np.max(energies)) if len(energies) > 0 else 0.0

        # Adaptive threshold: slightly above background floor, scaled to vocal activity
        noise_floor = float(np.percentile(energies, 15)) if len(energies) > 0 else 0.0
        silence_thresh = max(0.002, noise_floor * 1.5, mean_energy * self.silence_threshold_ratio)

        # Identify silent frames
        is_silent = energies < silence_thresh
        hop_time_s = hop_len / float(sample_rate)

        # Group consecutive silent frames into distinct pause episodes
        pause_durations: List[float] = []
        current_silent_frames = 0

        for silent in is_silent:
            if silent:
                current_silent_frames += 1
            else:
                if current_silent_frames > 0:
                    pause_s = current_silent_frames * hop_time_s
                    if pause_s >= self.min_pause_duration_s:
                        pause_durations.append(round(pause_s, 3))
                    current_silent_frames = 0

        # Handle trailing silence
        if current_silent_frames > 0:
            pause_s = current_silent_frames * hop_time_s
            if pause_s >= self.min_pause_duration_s:
                pause_durations.append(round(pause_s, 3))

        pause_count = len(pause_durations)
        total_pause_duration = sum(pause_durations)
        avg_pause = (total_pause_duration / pause_count) if pause_count > 0 else 0.0
        longest_pause = max(pause_durations) if pause_durations else 0.0
        active_duration = max(0.0, total_duration - total_pause_duration)
        active_ratio = min(1.0, active_duration / max(0.01, total_duration))
        pause_rate_per_min = (pause_count / max(0.01, total_duration)) * 60.0

        # Observable feedback description
        if pause_count == 0:
            feedback = "Continuous vocalization with no extended pauses detected."
        elif avg_pause <= 0.80 and active_ratio >= 0.70:
            feedback = f"Balanced pacing with natural conversational pauses (average pause: {avg_pause:.1f}s)."
        elif longest_pause >= 2.5:
            feedback = f"Noticeable extended pauses observed between spoken segments (longest pause: {longest_pause:.1f}s)."
        else:
            feedback = f"Frequent observable pauses detected during the response ({pause_count} pauses; avg: {avg_pause:.1f}s)."

        return {
            "total_duration_seconds": round(total_duration, 2),
            "pause_count": pause_count,
            "total_pause_duration": round(total_pause_duration, 2),
            "average_pause_duration": round(avg_pause, 2),
            "longest_pause": round(longest_pause, 2),
            "speech_active_duration": round(active_duration, 2),
            "speech_active_ratio": round(active_ratio, 3),
            "pause_rate_per_minute": round(pause_rate_per_min, 1),
            "feedback": feedback
        }
