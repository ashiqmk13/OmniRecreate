import os
import subprocess
from config import OUTPUT_DIR, TEMP_DIR

class Compositor:
    def __init__(self):
        pass

    def assemble_final_video(
        self,
        scene_visual_clips,
        voice_audio_clips,
        sfx_audio_clips,
        subtitle_ass_path=None,
        output_filename="recreated_video.mp4",
        progress_callback=None
    ):
        """
        Assembles visual clips, voice stem, and SFX stem with dynamic subtitles into a single final MP4.
        STRICT REQUIREMENT: NO BACKGROUND MUSIC ALLOWED!
        """
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        
        if progress_callback:
            progress_callback("Stitching video scenes together...", 85)

        # 1. Prepare video concat file
        concat_list_path = os.path.join(TEMP_DIR, "video_concat.txt")
        with open(concat_list_path, "w", encoding="utf-8") as f:
            for clip in scene_visual_clips:
                clean_path = os.path.abspath(clip).replace("\\", "/")
                f.write(f"file '{clean_path}'\n")

        raw_video_path = os.path.join(TEMP_DIR, "raw_concatenated_video.mp4")
        cmd_concat = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list_path,
            "-c", "copy", raw_video_path
        ]
        subprocess.run(cmd_concat, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if progress_callback:
            progress_callback("Mixing voiceover and SFX audio tracks (NO MUSIC)...", 90)

        # 2. Prepare audio concat / mix (Voice + SFX only)
        # Voice master track
        voice_concat_path = os.path.join(TEMP_DIR, "voice_concat.txt")
        with open(voice_concat_path, "w", encoding="utf-8") as f:
            for v_clip in voice_audio_clips:
                clean_v = os.path.abspath(v_clip).replace("\\", "/")
                f.write(f"file '{clean_v}'\n")

        voice_master_path = os.path.join(TEMP_DIR, "voice_master.wav")
        cmd_voice_concat = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", voice_concat_path,
            "-c", "copy", voice_master_path
        ]
        subprocess.run(cmd_voice_concat, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # SFX master track
        sfx_concat_path = os.path.join(TEMP_DIR, "sfx_concat.txt")
        with open(sfx_concat_path, "w", encoding="utf-8") as f:
            for s_clip in sfx_audio_clips:
                clean_s = os.path.abspath(s_clip).replace("\\", "/")
                f.write(f"file '{clean_s}'\n")

        sfx_master_path = os.path.join(TEMP_DIR, "sfx_master.wav")
        cmd_sfx_concat = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", sfx_concat_path,
            "-c", "copy", sfx_master_path
        ]
        subprocess.run(cmd_sfx_concat, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # 3. Mix Voice + SFX into audio master (strictly no music!)
        audio_master_path = os.path.join(TEMP_DIR, "audio_master_no_music.wav")
        cmd_mix = [
            "ffmpeg", "-y", "-i", voice_master_path, "-i", sfx_master_path,
            "-filter_complex", "[0:a]volume=1.2[v];[1:a]volume=0.5[s];[v][s]amix=inputs=2:duration=first[a]",
            "-map", "[a]", audio_master_path
        ]
        subprocess.run(cmd_mix, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if not os.path.exists(audio_master_path):
            audio_master_path = voice_master_path

        if progress_callback:
            progress_callback("Applying dynamic subtitle overlays & exporting master video...", 95)

        # 4. Final assembly with video + audio + subtitles
        vf_filters = []
        if subtitle_ass_path and os.path.exists(subtitle_ass_path):
            escaped_sub = os.path.abspath(subtitle_ass_path).replace("\\", "/").replace(":", "\\:")
            vf_filters.append(f"subtitles='{escaped_sub}'")

        cmd_final = [
            "ffmpeg", "-y", "-i", raw_video_path, "-i", audio_master_path
        ]
        
        if vf_filters:
            cmd_final.extend(["-vf", ",".join(vf_filters)])

        cmd_final.extend([
            "-c:v", "libx264", "-preset", "fast", "-crf", "22",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest", output_path
        ])

        res = subprocess.run(cmd_final, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res.returncode != 0:
            # Fallback direct mux without subtitle filter if libass error
            cmd_fallback = [
                "ffmpeg", "-y", "-i", raw_video_path, "-i", audio_master_path,
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", output_path
            ]
            subprocess.run(cmd_fallback, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if progress_callback:
            progress_callback("Master video export finished!", 100)

        return output_path
