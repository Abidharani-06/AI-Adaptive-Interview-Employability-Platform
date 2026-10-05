"""
Speech-to-Text Transcription Module
-----------------------------------
Transcribes interview speech from pre-recorded audio files or live microphone input.
Supports pluggable backends (Whisper, SpeechRecognition, HuggingFace Transformers, or deterministic fallback).
Handles edge cases: empty audio, silent recordings, missing files, microphone unavailability.
"""

import os
import sys
import tempfile
from pathlib import Path
from typing import Dict, Optional, Tuple, Any, Union
import numpy as np

# Local import of audio loader
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

from speech_features import load_audio


class SpeechToTextTranscriber:
    """
    Central speech-to-text transcriber for the interview platform.
    """

    def __init__(self, backend: str = "auto", whisper_model: str = "base"):
        """
        Parameters:
        - backend: "auto", "whisper", "speech_recognition", "transformers", or "mock"
        - whisper_model: Model name for Whisper ("tiny", "base", "small")
        """
        self.backend = backend
        self.whisper_model = whisper_model
        self._cached_model = None

    def transcribe_file(
        self,
        audio_path: Union[str, Path],
        mock_transcript: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transcribes speech from an audio file.

        Parameters:
        - audio_path: Path to WAV, MP3, or supported audio file.
        - mock_transcript: Optional text string to use when external ASR is offline or mocked for testing.
        """
        p = Path(audio_path)
        if not p.exists() or not p.is_file():
            return {
                "transcript": "",
                "duration_seconds": 0.0,
                "word_count": 0,
                "status": "file_not_found",
                "error": f"Audio file not found: {audio_path}"
            }

        # Validate and read audio to measure duration
        try:
            samples, sr = load_audio(p)
            duration_s = round(len(samples) / float(sr), 2) if samples is not None else 0.0
        except Exception as e:
            return {
                "transcript": "",
                "duration_seconds": 0.0,
                "word_count": 0,
                "status": "corrupt_audio",
                "error": f"Failed to decode audio file: {str(e)}"
            }

        if samples is None or len(samples) == 0:
            return {
                "transcript": "",
                "duration_seconds": 0.0,
                "word_count": 0,
                "status": "empty_recording",
                "error": "Audio contains zero samples."
            }

        # If a specific mock transcript was supplied, return it with status="mocked"
        if mock_transcript is not None:
            words = mock_transcript.strip().split()
            return {
                "transcript": mock_transcript.strip(),
                "duration_seconds": duration_s,
                "word_count": len(words),
                "status": "mocked",
                "backend": "mock_transcription"
            }

        # Check for pure silence / near-zero energy
        rms = float(np.sqrt(np.mean(samples * samples)))
        if rms < 0.001:
            return {
                "transcript": "",
                "duration_seconds": duration_s,
                "word_count": 0,
                "status": "no_speech_detected",
                "error": None
            }

        # Attempt transcription via backends
        transcript_text = None
        used_backend = "unknown"

        # 1. Try SpeechRecognition
        if self.backend in ("auto", "speech_recognition"):
            try:
                import speech_recognition as sr_lib
                r = sr_lib.Recognizer()
                with sr_lib.AudioFile(str(p)) as source:
                    audio_data = r.record(source)
                # Attempt offline whisper via speech_recognition if configured
                try:
                    text = r.recognize_whisper(audio_data, model=self.whisper_model)
                    transcript_text = text.strip()
                    used_backend = "speech_recognition_whisper"
                except Exception:
                    # Fallback to Google recognizer if online
                    try:
                        text = r.recognize_google(audio_data)
                        transcript_text = text.strip()
                        used_backend = "speech_recognition_google"
                    except Exception:
                        pass
            except Exception:
                pass

        # 2. Try Whisper direct library
        if transcript_text is None and self.backend in ("auto", "whisper"):
            try:
                import whisper
                if self._cached_model is None:
                    self._cached_model = whisper.load_model(self.whisper_model)
                res = self._cached_model.transcribe(str(p))
                transcript_text = res.get("text", "").strip()
                used_backend = "whisper_direct"
            except Exception:
                pass

        # 3. Fallback when offline or no models downloaded
        if transcript_text is None:
            return {
                "transcript": "",
                "duration_seconds": duration_s,
                "word_count": 0,
                "status": "offline_no_transcriber",
                "error": "No local transcription model available (Whisper or online SpeechRecognition). Provide mock_transcript or install whisper model."
            }

        words = transcript_text.split()
        return {
            "transcript": transcript_text,
            "duration_seconds": duration_s,
            "word_count": len(words),
            "status": "success",
            "backend": used_backend
        }

    def record_and_transcribe(
        self,
        duration_seconds: float = 5.0,
        sample_rate: int = 16000,
        mock_transcript: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Records live audio from the system microphone and transcribes it.
        Handles microphone unavailable and permission denied gracefully.
        """
        temp_wav = None
        try:
            import sounddevice as sd
            from scipy.io import wavfile

            # Test microphone access
            recorded_samples = sd.rec(
                int(duration_seconds * sample_rate),
                samplerate=sample_rate,
                channels=1,
                dtype="float32"
            )
            sd.wait()

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
                temp_wav = tf.name

            int16_samples = np.int16(np.clip(recorded_samples * 32767.0, -32768, 32767))
            wavfile.write(temp_wav, sample_rate, int16_samples)

            result = self.transcribe_file(temp_wav, mock_transcript=mock_transcript)
            return result
        except Exception as e:
            return {
                "transcript": "",
                "duration_seconds": 0.0,
                "word_count": 0,
                "status": "mic_unavailable",
                "error": f"Microphone capture error: {str(e)}"
            }
        finally:
            if temp_wav and os.path.exists(temp_wav):
                try:
                    os.remove(temp_wav)
                except Exception:
                    pass
