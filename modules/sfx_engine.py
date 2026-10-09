import os
import subprocess
from config import TEMP_DIR

class SFXEngine:
    def __init__(self):
        self.sfx_cache = {}

    def generate_sfx(self, sfx_prompt, duration_seconds=2.0, scene_id=1):
        """
        Generates or synthesizes a targeted Sound Effect (SFX) audio track.
        Returns path to WAV audio file.
        """
        output_filename = f"sfx_scene_{scene_id}.wav"
        output_path = os.path.join(TEMP_DIR, output_filename)
        
        prompt_lower = sfx_prompt.lower()
        
        # 1. Procedural SFX generation via FFmpeg audio synthesis filters
        if "boom" in prompt_lower or "impact" in prompt_lower:
            # Low frequency decaying bass impact boom
            cmd = [
                "ffmpeg", "-y", "-f", "lavfi",
                "-i", f"sine=frequency=60:duration={duration_seconds},afireq=gain=-10,volume=3.0,aecho=0.8:0.88:60:0.4",
                "-ar", "24000", "-ac", "2", output_path
            ]
        elif "swoosh" in prompt_lower or "tech" in prompt_lower or "riser" in prompt_lower:
            # Sweeping frequency filter for tech swoosh
            cmd = [
                "ffmpeg", "-y", "-f", "lavfi",
                "-i", f"anoisesrc=d={duration_seconds}:c=white:r=24000,bandpass=f=1000:width_type=h:w=500,volume=2.0",
                "-ar", "24000", "-ac", "2", output_path
            ]
        elif "wind" in prompt_lower or "ambient" in prompt_lower or "rumble" in prompt_lower:
            # Ambient low rumble
            cmd = [
                "ffmpeg", "-y", "-f", "lavfi",
                "-i", f"anoisesrc=d={duration_seconds}:c=pink:r=24000,lowpass=f=300,volume=1.5",
                "-ar", "24000", "-ac", "2", output_path
            ]
        else:
            # Subtle UI click / pulse
            cmd = [
                "ffmpeg", "-y", "-f", "lavfi",
                "-i", f"sine=frequency=440:duration={min(1.0, duration_seconds)},volume=1.0",
                "-ar", "24000", "-ac", "2", output_path
            ]

        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res.returncode == 0 and os.path.exists(output_path):
            return output_path
            
        # Silent fallback WAV
        cmd_silent = [
            "ffmpeg", "-y", "-f", "lavfi",
            "-i", f"anullsrc=r=24000:cl=stereo:d={duration_seconds}",
            output_path
        ]
        subprocess.run(cmd_silent, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return output_path
