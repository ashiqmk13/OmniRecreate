import os
import torch

# Base Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
TEMP_DIR = os.path.join(BASE_DIR, "temp")
MODELS_DIR = os.path.join(BASE_DIR, "models")
CACHE_DIR = os.path.join(BASE_DIR, "cache")

for path in [OUTPUT_DIR, TEMP_DIR, MODELS_DIR, CACHE_DIR]:
    os.makedirs(path, exist_ok=True)

# Device configuration
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
FP16 = torch.cuda.is_available()

# Default Settings
DEFAULT_SETTINGS = {
    "target_duration_minutes": 5, # Can be up to 25+ minutes
    "lock_facial_features": True,  # LOCKED by default (No human facial features generated)
    "voice_engine": "kokoro",      # Options: kokoro, chatterbox, edge_tts, pyttsx3
    "voice_name": "af_heart",      # Kokoro voice sample (af_heart, am_adam, etc.)
    "image_generator": "sdxl_lightning", # sdxl_lightning, animatediff, procedural
    "enable_sfx": True,
    "enable_subtitles": True,
    "subtitle_style": "bold_yellow",
    "strict_no_music": True        # LOCKED: Never add background music
}

# Facial Feature Enforcement Prompts
FACELESS_POSITIVE_PROMPT = "faceless human, smooth featureless silhouette, anonymous mannequin style, minimalist character, clean aesthetics, atmospheric lighting"
FACELESS_NEGATIVE_PROMPT = "facial features, detailed face, eyes, nose, mouth, lips, eyebrows, teeth, realistic face, facial expression"

UNLOCKED_FACE_PROMPT = "detailed character portrait, expressive facial features, cinematic lighting"

# Text Subtitle Presets
SUBTITLE_PRESETS = {
    "bold_yellow": {
        "fontsize": 28,
        "color": "&H0000FFFF",  # Yellow in BGR ASS format
        "outline_color": "&H00000000",
        "outline": 2,
        "font": "Arial",
        "bold": 1
    },
    "cyber_cyan": {
        "fontsize": 30,
        "color": "&H00FFFF00",  # Cyan in BGR ASS format
        "outline_color": "&H00111111",
        "outline": 3,
        "font": "Impact",
        "bold": 1
    },
    "minimal_white": {
        "fontsize": 24,
        "color": "&H00FFFFFF",  # White
        "outline_color": "&H00000000",
        "outline": 1,
        "font": "Helvetica",
        "bold": 0
    }
}
