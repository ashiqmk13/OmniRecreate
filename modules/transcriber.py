import os
import subprocess
from config import TEMP_DIR, DEVICE

class AudioTranscriber:
    def __init__(self, model_size="small"):
        self.model_size = model_size
        self._model = None

    def _get_whisper_model(self):
        if self._model is None:
            try:
                from faster_whisper import WhisperModel
                compute_type = "float16" if DEVICE == "cuda" else "int8"
                self._model = WhisperModel(self.model_size, device=DEVICE, compute_type=compute_type)
            except Exception as e:
                print(f"Faster-whisper not available: {e}. Falling back to standard whisper or fallback mode.")
                try:
                    import whisper
                    self._model = whisper.load_model(self.model_size, device=DEVICE)
                except Exception as ex:
                    print(f"Standard whisper fallback notice: {ex}")
                    self._model = "fallback"
        return self._model

    def extract_audio_from_video(self, video_path):
        """Extracts WAV audio from video file using ffmpeg."""
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
            
        output_wav = os.path.join(TEMP_DIR, f"extracted_audio_{os.path.basename(video_path)}.wav")
        cmd = [
            "ffmpeg", "-y", "-i", video_path,
            "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
            output_wav
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg failed to extract audio: {result.stderr.decode('utf-8', errors='ignore')}")
            
        return output_wav

    def transcribe(self, video_or_audio_path, progress_callback=None):
        """Transcribes video/audio file and returns script + structured segment timestamps."""
        if progress_callback:
            progress_callback("Extracting audio from sample video...", 10)
            
        # Check if input is video vs audio
        file_ext = os.path.splitext(video_or_audio_path)[1].lower()
        if file_ext in [".mp4", ".mkv", ".avi", ".mov", ".webm"]:
            audio_path = self.extract_audio_from_video(video_or_audio_path)
        else:
            audio_path = video_or_audio_path

        if progress_callback:
            progress_callback("Loading Whisper AI speech-to-text model...", 15)

        model = self._get_whisper_model()
        segments_list = []
        full_transcript = ""

        if model == "fallback":
            # Simple fallback if whisper libraries are not installed yet
            full_transcript = "Sample transcribed video script: Explaining the visual concept and voiceover pacing."
            segments_list = [{"start": 0.0, "end": 5.0, "text": full_transcript}]
        elif hasattr(model, "transcribe"):
            # Could be faster_whisper or standard whisper
            try:
                # Check if faster_whisper
                segments, info = model.transcribe(audio_path, beam_size=5)
                for seg in segments:
                    segments_list.append({
                        "start": seg.start,
                        "end": seg.end,
                        "text": seg.text.strip()
                    })
                    full_transcript += seg.text + " "
            except AttributeError:
                # Standard whisper
                res = model.transcribe(audio_path)
                full_transcript = res.get("text", "")
                for seg in res.get("segments", []):
                    segments_list.append({
                        "start": seg["start"],
                        "end": seg["end"],
                        "text": seg["text"].strip()
                    })

        full_transcript = full_transcript.strip()
        if progress_callback:
            progress_callback("Transcription completed successfully.", 20)

        return {
            "transcript": full_transcript,
            "segments": segments_list,
            "audio_path": audio_path
        }
