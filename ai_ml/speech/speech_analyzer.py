"""
Master Speech Analysis Module
-----------------------------
Unified orchestrator for Speech-to-Text, Audio Energy, Pause Analysis,
Filler Word Detection, and Fluency & Continuity Metrics.

Features:
- File-based and microphone-based audio ingestion
- Extraction of observable speech signals across time and text
- Graceful error handling for missing/corrupt audio, silence, or missing hardware
- Strictly non-psychological, observable feedback reports
"""

import os
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
import numpy as np

# Resolve local speech modules
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

from speech_features import load_audio, AudioFeatureExtractor
from pause_analyzer import PauseAnalyzer
from filler_detector import FillerDetector
from fluency_analysis import FluencyAnalyzer
from speech_to_text import SpeechToTextTranscriber


class SpeechAnalyzer:
    """
    Central orchestrator combining acoustic features, pause timing,
    lexical filler detection, and speech delivery rate into a unified assessment.
    """

    def __init__(
        self,
        stt_backend: str = "auto",
        whisper_model: str = "base",
        custom_fillers: Optional[List[str]] = None
    ):
        self.stt = SpeechToTextTranscriber(backend=stt_backend, whisper_model=whisper_model)
        self.feature_extractor = AudioFeatureExtractor()
        self.pause_analyzer = PauseAnalyzer()
        self.filler_detector = FillerDetector(custom_fillers=custom_fillers)
        self.fluency_analyzer = FluencyAnalyzer()

    def analyze_audio_file(
        self,
        audio_path: Union[str, Path],
        mock_transcript: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyzes an audio file end-to-end.
        """
        p = Path(audio_path)
        if not p.exists() or not p.is_file():
            return {
                "success": False,
                "error": f"Audio file not found: {audio_path}",
                "transcript": "",
                "duration_seconds": 0.0,
                "speaking_rate_wpm": 0.0,
                "pause_count": 0,
                "average_pause_seconds": 0.0,
                "fillers_per_100_words": 0.0,
                "energy_consistency_percentage": 0.0,
                "speech_continuity_percentage": 0.0,
                "observable_feedback": [f"Audio file '{audio_path}' could not be located."],
                "formatted_report": "Speech Analysis Assessment\n--------------------------\nStatus: File not found.\n"
            }

        try:
            samples, sr = load_audio(p)
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to load audio: {str(e)}",
                "transcript": "",
                "duration_seconds": 0.0,
                "speaking_rate_wpm": 0.0,
                "pause_count": 0,
                "average_pause_seconds": 0.0,
                "fillers_per_100_words": 0.0,
                "energy_consistency_percentage": 0.0,
                "speech_continuity_percentage": 0.0,
                "observable_feedback": [f"Failed to decode audio file: {str(e)}"],
                "formatted_report": "Speech Analysis Assessment\n--------------------------\nStatus: Decode failure.\n"
            }

        return self.analyze_signal(samples, sr, mock_transcript=mock_transcript, file_source=str(p))

    def analyze_signal(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        mock_transcript: Optional[str] = None,
        file_source: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyzes in-memory audio samples array.
        """
        if audio_data is None or len(audio_data) == 0:
            return {
                "success": False,
                "error": "Empty audio buffer received.",
                "transcript": "",
                "duration_seconds": 0.0,
                "speaking_rate_wpm": 0.0,
                "pause_count": 0,
                "average_pause_seconds": 0.0,
                "fillers_per_100_words": 0.0,
                "energy_consistency_percentage": 0.0,
                "speech_continuity_percentage": 0.0,
                "observable_feedback": ["Audio signal is empty or contains no samples."],
                "formatted_report": "Speech Analysis Assessment\n--------------------------\nStatus: Empty audio.\n"
            }

        # 1. Acoustic Energy Features
        audio_metrics = self.feature_extractor.analyze_audio(audio_data, sample_rate)
        duration_s = audio_metrics.get("duration_seconds", 0.0)

        # 2. Pause Analysis
        pause_metrics = self.pause_analyzer.analyze_signal(audio_data, sample_rate)

        # 3. Transcription
        if file_source and os.path.exists(file_source):
            stt_result = self.stt.transcribe_file(file_source, mock_transcript=mock_transcript)
        else:
            # Write temporary WAV for STT recognizers
            temp_wav = None
            try:
                from scipy.io import wavfile
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
                    temp_wav = tf.name
                int16_samples = np.int16(np.clip(audio_data * 32767.0, -32768, 32767))
                wavfile.write(temp_wav, sample_rate, int16_samples)
                stt_result = self.stt.transcribe_file(temp_wav, mock_transcript=mock_transcript)
            finally:
                if temp_wav and os.path.exists(temp_wav):
                    try:
                        os.remove(temp_wav)
                    except Exception:
                        pass

        transcript = stt_result.get("transcript", "")

        # 4. Filler Word Detection
        filler_metrics = self.filler_detector.analyze(transcript)

        # 5. Fluency & Speaking Rate
        fluency_metrics = self.fluency_analyzer.analyze_fluency(
            transcript=transcript,
            duration_seconds=duration_s,
            pause_metrics=pause_metrics,
            filler_metrics=filler_metrics
        )

        # Compile observable feedback
        feedback_list = []
        if transcript:
            feedback_list.append(fluency_metrics.get("feedback", "Speaking rate evaluated."))
            feedback_list.append(pause_metrics.get("feedback", "Pause distribution analyzed."))
            feedback_list.append(filler_metrics.get("feedback", "Filler frequency measured."))
            feedback_list.append(audio_metrics.get("feedback", "Energy consistency measured."))
        else:
            if audio_metrics.get("average_energy", 0.0) < 0.002:
                feedback_list.append("Audio was silent or below vocal detection threshold.")
            else:
                feedback_list.append("No intelligible speech transcribed from the audio signal.")

        summary = {
            "success": True,
            "transcript": transcript,
            "duration_seconds": duration_s,
            "word_count": fluency_metrics["word_count"],
            "speaking_rate_wpm": fluency_metrics["words_per_minute"],
            "pacing_category": fluency_metrics["pacing_category"],
            "pause_count": pause_metrics["pause_count"],
            "average_pause_seconds": pause_metrics["average_pause_duration"],
            "longest_pause_seconds": pause_metrics["longest_pause"],
            "total_pause_seconds": pause_metrics["total_pause_duration"],
            "speech_active_ratio": pause_metrics["speech_active_ratio"],
            "speech_active_percentage": round(pause_metrics["speech_active_ratio"] * 100, 1),
            "filler_count": filler_metrics["filler_count"],
            "fillers_per_100_words": filler_metrics["fillers_per_100_words"],
            "detected_fillers": filler_metrics["detected_fillers"],
            "most_frequent_fillers": filler_metrics["most_frequent_fillers"],
            "energy_consistency_percentage": audio_metrics["energy_consistency_percentage"],
            "average_energy": audio_metrics["average_energy"],
            "speech_continuity_percentage": fluency_metrics["speech_continuity_percentage"],
            "observable_feedback": feedback_list,
            "metrics": {
                "stt": stt_result,
                "audio": audio_metrics,
                "pauses": pause_metrics,
                "fillers": filler_metrics,
                "fluency": fluency_metrics
            }
        }

        summary["formatted_report"] = self.generate_report_text(summary)
        self.last_summary = summary
        return summary

    def get_summary(self) -> Optional[Dict[str, Any]]:
        """Returns the most recent speech assessment summary."""
        return getattr(self, "last_summary", None)

    def record_and_analyze(
        self,
        duration_seconds: float = 5.0,
        sample_rate: int = 16000,
        mock_transcript: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Records live audio from the microphone and runs full speech analysis.
        Handles microphone missing or permission denied gracefully.
        """
        try:
            import sounddevice as sd
            recorded_samples = sd.rec(
                int(duration_seconds * sample_rate),
                samplerate=sample_rate,
                channels=1,
                dtype="float32"
            )
            sd.wait()
            samples = recorded_samples.flatten()
            return self.analyze_signal(samples, sample_rate, mock_transcript=mock_transcript)
        except Exception as e:
            return {
                "success": False,
                "error": f"Microphone recording error: {str(e)}",
                "transcript": "",
                "duration_seconds": 0.0,
                "speaking_rate_wpm": 0.0,
                "pause_count": 0,
                "average_pause_seconds": 0.0,
                "fillers_per_100_words": 0.0,
                "energy_consistency_percentage": 0.0,
                "speech_continuity_percentage": 0.0,
                "observable_feedback": [f"Microphone unavailable or permission denied: {str(e)}"],
                "formatted_report": "Speech Analysis Assessment\n--------------------------\nStatus: Microphone unavailable.\n"
            }

    def generate_report_text(self, summary: Optional[Dict[str, Any]] = None) -> str:
        """
        Generates a clean, readable text assessment conforming to Phase 6 specifications.
        """
        if summary is None:
            return "No speech analysis summary provided."

        lines = [
            "============================================================",
            "                 SPEECH ANALYSIS ASSESSMENT                 ",
            "============================================================",
            f"Transcript Snippet : \"{(summary['transcript'][:80] + '...') if len(summary['transcript']) > 80 else summary['transcript']}\"",
            f"Speaking Rate      : {summary['speaking_rate_wpm']} WPM ({summary.get('pacing_category', '').replace('_', ' ').title()})",
            f"Pause Count        : {summary['pause_count']} pauses",
            f"Average Pause      : {summary['average_pause_seconds']:.2f} sec (Longest: {summary.get('longest_pause_seconds', 0.0):.2f} sec)",
            f"Speech Active Ratio: {summary.get('speech_active_percentage', 0.0)}%",
            f"Filler Word Count  : {summary['filler_count']} ({summary['fillers_per_100_words']} per 100 words)",
            f"Energy Consistency : {summary['energy_consistency_percentage']:.1f}%",
            f"Speech Continuity  : {summary['speech_continuity_percentage']:.1f}%",
            "------------------------------------------------------------",
            "Observable Acoustic & Verbal Feedback:"
        ]
        for fb in summary.get("observable_feedback", []):
            lines.append(f"- {fb}")

        if summary.get("most_frequent_fillers"):
            filler_str = ", ".join([f"'{k}': {v}x" for k, v in summary["most_frequent_fillers"][:4]])
            lines.append(f"- Top Detected Fillers: {filler_str}")

        lines.append("============================================================\n")
        return "\n".join(lines)
