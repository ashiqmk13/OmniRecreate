import os
import subprocess
import wave
import contextlib
from config import TEMP_DIR, DEVICE

class TTSEngine:
    def __init__(self, engine_type="kokoro", voice_name="af_heart"):
        self.engine_type = engine_type.lower()
        self.voice_name = voice_name
        self._kokoro_pipeline = None

    def _init_kokoro(self):
        if self._kokoro_pipeline is None:
            try:
                # Attempt importing kokoro or kokoro-onnx
                from kokoro import KPipeline
                self._kokoro_pipeline = KPipeline(lang_code='a') # 'a' for American English
            except Exception as e:
                print(f"Kokoro TTS native load fallback note: {e}")
                self._kokoro_pipeline = "fallback"

    def synthesize(self, text, output_filename):
        """
        Synthesizes spoken audio from text and saves to WAV file.
        Returns: dict { 'audio_path': path, 'duration_seconds': float }
        """
        output_path = os.path.join(TEMP_DIR, output_filename)
        
        if self.engine_type == "kokoro":
            success = self._synthesize_kokoro(text, output_path)
            if not success:
                success = self._synthesize_edge_or_pyttsx3(text, output_path)
        else:
            success = self._synthesize_edge_or_pyttsx3(text, output_path)

        if not success or not os.path.exists(output_path):
            # Final dummy WAV generator for extreme environment compatibility
            self._create_silent_or_procedural_wav(text, output_path)

        # Get audio duration
        duration = self.get_wav_duration(output_path)
        return {
            "audio_path": output_path,
            "duration_seconds": duration,
            "text": text
        }

    def _synthesize_kokoro(self, text, output_path):
        """Attempts synthesis using Kokoro-TTS."""
        try:
            self._init_kokoro()
            if self._kokoro_pipeline != "fallback" and self._kokoro_pipeline is not None:
                import soundfile as sf
                generator = self._kokoro_pipeline(text, voice=self.voice_name, speed=1.0, split_pattern=r'\n+')
                audio_segments = []
                for _, _, audio in generator:
                    audio_segments.append(audio)
                if audio_segments:
                    import numpy as np
                    full_audio = np.concatenate(audio_segments)
                    sf.write(output_path, full_audio, 24000)
                    return True
        except Exception as e:
            print(f"Kokoro synthesis exception: {e}")
        return False

    def _synthesize_edge_or_pyttsx3(self, text, output_path):
        """Attempts edge-tts or pyttsx3 fallback synthesis."""
        # 1. Try edge-tts (Open Source Microsoft Voice Engine, offline/free)
        try:
            cmd = ["edge-tts", "--text", text, "--write-media", output_path]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=15)
            if res.returncode == 0 and os.path.exists(output_path):
                return True
        except Exception:
            pass

        # 2. Try pyttsx3 (System SAPI5/eSpeak TTS)
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.save_to_file(text, output_path)
            engine.runAndWait()
            if os.path.exists(output_path):
                return True
        except Exception:
            pass

        return False

    def _create_silent_or_procedural_wav(self, text, output_path):
        """Creates a timed audio file matching estimated speech length (~150 words per min)."""
        words = len(text.split())
        est_seconds = max(2.0, (words / 150.0) * 60.0)
        
        # Generate clean sine audio beep / speech simulation tone via ffmpeg
        cmd = [
            "ffmpeg", "-y", "-f", "lavfi",
            "-i", f"sine=frequency=300:duration={est_seconds}",
            "-ar", "24000", "-ac", "1",
            output_path
        ]
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def get_wav_duration(self, wav_path):
        """Calculates precise audio duration in seconds."""
        if not os.path.exists(wav_path):
            return 3.0
        try:
            cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", wav_path]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if res.returncode == 0 and res.stdout.strip():
                return float(res.stdout.strip())
        except Exception:
            pass
            
        try:
            with contextlib.closing(wave.open(wav_path, 'r')) as f:
                frames = f.getnframes()
                rate = f.getframerate()
                return frames / float(rate)
        except Exception:
            return 3.0
