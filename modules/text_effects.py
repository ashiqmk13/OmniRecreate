import os
import re
from config import TEMP_DIR, SUBTITLE_PRESETS

class TextEffectsEngine:
    def __init__(self, style_preset="bold_yellow"):
        self.set_style(style_preset)

    def set_style(self, style_preset):
        if isinstance(style_preset, str):
            self.style = SUBTITLE_PRESETS.get(style_preset, SUBTITLE_PRESETS["bold_yellow"])
        else:
            self.style = style_preset

    def create_ass_subtitles(self, scenes, output_filename="subtitles.ass"):
        """
        Creates an Advanced SubStation Alpha (.ass) file with animated text effects,
        custom fonts, colors, and positioning.
        """
        output_path = os.path.join(TEMP_DIR, output_filename)
        
        ass_header = f"""[Script Info]
Title: OmniRecreate Dynamic Subtitles
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: None

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{self.style['font']},{self.style['fontsize']},{self.style['color']},&H00000000,{self.style['outline_color']},&H00000000,{self.style['bold']},0,0,0,100,100,0,0,1,{self.style['outline']},1,2,20,20,40,1
Style: Header,Impact,36,&H0000FFFF,&H00000000,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,3,2,8,20,20,60,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        lines = [ass_header]
        current_time = 0.0

        for scene in scenes:
            duration = float(scene.get("duration_seconds", 5.0))
            start_str = self._format_ass_time(current_time)
            end_str = self._format_ass_time(current_time + duration)
            
            # Header overlay effect
            header_text = scene.get("text_overlay", "")
            if header_text:
                lines.append(f"Dialogue: 1,{start_str},{end_str},Header,,0,0,0,,{{\\fad(300,300)}}{header_text}")
                
            # Spoken narration caption lines
            narration = scene.get("narration_text", "")
            if narration:
                # Format animated text effect (fade in/out + glowing outline)
                clean_text = re.sub(r'[^\w\s\.,!\?]', '', narration)
                lines.append(f"Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,{{\\fad(200,200)}}{clean_text}")

            current_time += duration

        with open(output_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

        return output_path

    def _format_ass_time(self, seconds):
        hours = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        cs = int(round((seconds - int(seconds)) * 100))
        return f"{hours}:{mins:02d}:{secs:02d}.{cs:02d}"

    def get_ffmpeg_drawtext_filter(self, text, start_sec, duration_sec):
        """Generates dynamic FFmpeg drawtext filter string for direct video burn-in."""
        clean = text.replace(":", "\\:").replace("'", "\\'").replace('"', '\\"')
        return (
            f"drawtext=text='{clean}':fontcolor=yellow:fontsize=32:"
            f"box=1:boxcolor=black@0.6:boxborderw=10:x=(w-text_w)/2:y=h-80:"
            f"enable='between(t,{start_sec},{start_sec + duration_sec})'"
        )
