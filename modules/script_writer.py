import json
import re
import math
from config import FACELESS_POSITIVE_PROMPT, UNLOCKED_FACE_PROMPT

class ScriptWriter:
    def __init__(self, llm_provider="auto"):
        self.llm_provider = llm_provider

    def generate_script_structure(
        self,
        sample_transcript,
        user_instructions,
        style_profile,
        target_duration_minutes=5,
        lock_facial_features=True,
        character_reference_desc=""
    ):
        """
        Generates a complete multi-scene video breakdown matching target_duration_minutes.
        Returns a list of dicts: [ {scene_id, duration_seconds, narration_text, visual_prompt, sfx_prompt, text_overlay}, ... ]
        """
        target_total_seconds = target_duration_minutes * 60
        # Average scene duration ~ 8-12 seconds
        avg_scene_duration = 10.0
        num_scenes = max(1, math.ceil(target_total_seconds / avg_scene_duration))
        
        art_style = style_profile.get("art_style", "Cinematic Dark")
        
        # Build facial feature rule
        if lock_facial_features:
            face_rule = FACELESS_POSITIVE_PROMPT
            if character_reference_desc:
                face_rule += f", matching character reference ({character_reference_desc})"
        else:
            face_rule = UNLOCKED_FACE_PROMPT
            if character_reference_desc:
                face_rule += f", consistent character appearance ({character_reference_desc})"

        # Attempt local LLM call if Ollama or Transformers available
        scenes = self._try_local_llm_generation(
            sample_transcript,
            user_instructions,
            art_style,
            target_duration_minutes,
            num_scenes,
            face_rule
        )

        if not scenes:
            # Fallback algorithmic script generation engine
            scenes = self._algorithmic_script_generation(
                sample_transcript,
                user_instructions,
                art_style,
                target_total_seconds,
                num_scenes,
                face_rule
            )

        # Enforce exact total duration matching
        calculated_total = sum(s["duration_seconds"] for s in scenes)
        if calculated_total > 0:
            scale_factor = target_total_seconds / calculated_total
            for s in scenes:
                s["duration_seconds"] = round(s["duration_seconds"] * scale_factor, 1)

        return {
            "total_duration_minutes": target_duration_minutes,
            "total_duration_seconds": target_total_seconds,
            "total_scenes": len(scenes),
            "art_style": art_style,
            "lock_facial_features": lock_facial_features,
            "scenes": scenes
        }

    def _try_local_llm_generation(self, transcript, instructions, art_style, duration_min, num_scenes, face_rule):
        """Attempts generation using local Ollama if available."""
        try:
            import requests
            prompt = f"""
You are an expert video producer. Generate a structured script for a {duration_min}-minute video ({num_scenes} scenes).
Context from sample: {transcript[:500]}
User Instructions: {instructions}
Visual Style: {art_style}
Facial Rule: {face_rule}

Output ONLY valid JSON array of scenes format:
[
  {{
    "scene_id": 1,
    "duration_seconds": 10.0,
    "narration_text": "Spoken voiceover text here...",
    "visual_prompt": "Detailed AI image/video prompt...",
    "sfx_prompt": "Sound effect description or none",
    "text_overlay": "Key text caption header"
  }}
]
"""
            res = requests.post("http://localhost:11434/api/generate", json={
                "model": "qwen2.5:7b",
                "prompt": prompt,
                "stream": False
            }, timeout=3)
            
            if res.status_code == 200:
                text = res.json().get("response", "")
                json_match = re.search(r'\[.*\]', text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(0))
        except Exception:
            pass
        return None

    def _algorithmic_script_generation(
        self,
        transcript,
        instructions,
        art_style,
        target_total_seconds,
        num_scenes,
        face_rule
    ):
        """High quality algorithmic script synthesizer for any duration (e.g. 5m to 25m+)."""
        base_topic = instructions if instructions else "Advanced AI & Technological Future"
        sample_words = transcript.split() if transcript else []
        
        scenes = []
        scene_duration = target_total_seconds / num_scenes
        
        # Audio SFX library triggers
        sfx_catalog = [
            "deep cinematic impact boom",
            "futuristic digital tech swoosh",
            "ambient wind rumble sound effect",
            "glitch interface sound effect",
            "subtle heart beat pulse sfx",
            "fast data stream rise effect",
            "dramatic trailer riser effect",
            "soft keyboard typing sound effect"
        ]

        # Key concepts for script expanding
        sections = [
            ("Introduction & Paradigm Shift", "Welcome to an extraordinary journey into innovation and breakthrough thinking."),
            ("Core Foundation & Principles", "To master this domain, we first examine the foundational mechanics driving transformation."),
            ("Deep Dive Analysis & Breakthroughs", "Analyzing the key variables reveals how complex dynamics create unprecedented value."),
            ("Real-world Practical Execution", "Applying these exact methodologies yields immediate efficiency and scalable impact."),
            ("Future Horizons & Strategic Conclusion", "As we look ahead, the trajectory is clear: innovation rewards those who build today.")
        ]

        for i in range(1, num_scenes + 1):
            sec_idx = min(len(sections) - 1, int((i - 1) / num_scenes * len(sections)))
            sec_title, sec_base = sections[sec_idx]
            
            # Words for narration
            narration = f"Section {sec_idx + 1}, Part {i}: {sec_base} {base_topic}. "
            if sample_words:
                sub_words = sample_words[(i*10) % len(sample_words) : ((i*10)+25) % len(sample_words)]
                if sub_words:
                    narration += " " + " ".join(sub_words)
                    
            # Visual prompt combining style + face lock + scene context
            visual_prompt = (
                f"{art_style}, {sec_title}, {base_topic}, scene {i}. "
                f"Atmospheric shot, cinematic lighting, 8k resolution, {face_rule}"
            )

            # SFX
            sfx = sfx_catalog[(i - 1) % len(sfx_catalog)]

            # Text overlay
            text_overlay = f"{sec_title.upper()} - PART {i}"

            scenes.append({
                "scene_id": i,
                "duration_seconds": round(scene_duration, 1),
                "narration_text": narration.strip(),
                "visual_prompt": visual_prompt,
                "sfx_prompt": sfx,
                "text_overlay": text_overlay
            })

        return scenes
