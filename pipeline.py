import os
import time
import threading
from config import DEFAULT_SETTINGS, OUTPUT_DIR
from modules.transcriber import AudioTranscriber
from modules.style_analyzer import StyleAnalyzer
from modules.script_writer import ScriptWriter
from modules.tts_engine import TTSEngine
from modules.sfx_engine import SFXEngine
from modules.text_effects import TextEffectsEngine
from modules.visual_generator import VisualGenerator
from modules.compositor import Compositor
from modules.progress_tracker import tracker

class VideoRecreationPipeline:
    def __init__(self):
        self.transcriber = AudioTranscriber()
        self.style_analyzer = StyleAnalyzer()
        self.script_writer = ScriptWriter()
        self.tts_engine = TTSEngine()
        self.sfx_engine = SFXEngine()
        self.text_effects = TextEffectsEngine()
        self.visual_generator = VisualGenerator()
        self.compositor = Compositor()

    def run_recreation(
        self,
        sample_video_path=None,
        visual_instructions="",
        target_duration_minutes=5,
        lock_facial_features=True,
        character_reference_path=None,
        voice_engine="kokoro",
        voice_name="af_heart",
        subtitle_style="bold_yellow",
        output_filename="recreated_video.mp4"
    ):
        """
        Executes complete video recreation workflow asynchronously while updating progress tracker.
        """
        try:
            tracker.start(total_steps=100)
            tracker.update("Analyzing input & initializing pipeline...", 5)

            # Step 1: Transcribe Sample Video
            sample_transcript = ""
            if sample_video_path and os.path.exists(sample_video_path):
                tracker.update("Transcribing sample video audio...", 10)
                transcription_res = self.transcriber.transcribe(
                    sample_video_path,
                    progress_callback=lambda msg, pct: tracker.update(msg, pct)
                )
                sample_transcript = transcription_res.get("transcript", "")
                tracker.log(f"Transcribed {len(sample_transcript.split())} words from sample video.")
            else:
                tracker.log("No sample video uploaded. Relying on visual instructions.")

            # Step 2: Analyze Visual Style
            tracker.update("Analyzing video style & visual cues...", 20)
            style_profile = self.style_analyzer.analyze_style(sample_video_path, visual_instructions)
            tracker.log(f"Inferred Visual Style: {style_profile.get('art_style')}")

            # Step 3: Script & Scene Breakdown Generation for target duration
            tracker.update(f"Generating script breakdown for {target_duration_minutes}-minute video...", 25)
            script_data = self.script_writer.generate_script_structure(
                sample_transcript=sample_transcript,
                user_instructions=visual_instructions,
                style_profile=style_profile,
                target_duration_minutes=target_duration_minutes,
                lock_facial_features=lock_facial_features,
                character_reference_desc="Custom character reference" if character_reference_path else ""
            )
            
            scenes = script_data.get("scenes", [])
            total_scenes = len(scenes)
            tracker.log(f"Script created with {total_scenes} scenes spanning {target_duration_minutes} minutes.")

            # Prepare per-scene generation loops
            scene_visuals = []
            voice_clips = []
            sfx_clips = []

            self.tts_engine.engine_type = voice_engine
            self.tts_engine.voice_name = voice_name
            self.text_effects.set_style(subtitle_style)

            start_scene_pct = 30.0
            end_scene_pct = 80.0
            pct_per_scene = (end_scene_pct - start_scene_pct) / max(1, total_scenes)

            for i, scene in enumerate(scenes, 1):
                if tracker.is_cancelled:
                    tracker.log("Task cancelled by user.")
                    return None

                curr_pct = start_scene_pct + (i - 1) * pct_per_scene
                tracker.update(
                    f"Processing Scene {i}/{total_scenes}",
                    curr_pct,
                    detail=f"Duration: {scene['duration_seconds']}s | Lock Face: {lock_facial_features}"
                )

                # A. Synthesize Voice Audio
                narration = scene.get("narration_text", "")
                tts_res = self.tts_engine.synthesize(narration, f"voice_scene_{i:03d}.wav")
                voice_clips.append(tts_res["audio_path"])

                # B. Synthesize Sound Effects (SFX) - STRICTLY NO MUSIC
                sfx_prompt = scene.get("sfx_prompt", "subtle swoosh")
                sfx_path = self.sfx_engine.generate_sfx(sfx_prompt, duration_seconds=scene["duration_seconds"], scene_id=i)
                sfx_clips.append(sfx_path)

                # C. Generate Visual Scene Video Clip
                visual_prompt = scene.get("visual_prompt", "")
                v_clip_path = self.visual_generator.generate_scene_visual(
                    visual_prompt=visual_prompt,
                    duration_seconds=scene["duration_seconds"],
                    scene_id=i,
                    lock_facial_features=lock_facial_features,
                    character_reference_image=character_reference_path,
                    aspect_ratio=style_profile.get("aspect_ratio", "16:9")
                )
                scene_visuals.append(v_clip_path)

            # Step 4: Create Animated Subtitles
            tracker.update("Generating dynamic text effects and subtitles...", 82)
            sub_path = self.text_effects.create_ass_subtitles(scenes, "master_subtitles.ass")

            # Step 5: Master Video Assembly via FFmpeg (STRICT NO MUSIC!)
            tracker.update("Assembling final video with audio & sfx stems...", 85)
            final_video_path = self.compositor.assemble_final_video(
                scene_visual_clips=scene_visuals,
                voice_audio_clips=voice_clips,
                sfx_audio_clips=sfx_clips,
                subtitle_ass_path=sub_path,
                output_filename=output_filename,
                progress_callback=lambda msg, pct: tracker.update(msg, pct)
            )

            tracker.finish(output_path=final_video_path)
            return final_video_path

        except Exception as e:
            tracker.fail(e)
            raise e
