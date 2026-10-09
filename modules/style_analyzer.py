import os
import cv2
import numpy as np
from config import TEMP_DIR

class StyleAnalyzer:
    def __init__(self):
        pass

    def extract_keyframes(self, video_path, num_frames=5):
        """Extracts N evenly spaced keyframes from the sample video."""
        if not os.path.exists(video_path):
            return []
            
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total_frames <= 0:
            cap.release()
            return []
            
        step = max(1, total_frames // num_frames)
        keyframes = []
        frame_idx = 0
        
        extracted_paths = []
        
        while cap.isOpened() and len(keyframes) < num_frames:
            ret, frame = cap.read()
            if not ret:
                break
            if frame_idx % step == 0:
                img_name = f"keyframe_{len(keyframes)}.jpg"
                img_path = os.path.join(TEMP_DIR, img_name)
                cv2.imwrite(img_path, frame)
                keyframes.append(frame)
                extracted_paths.append(img_path)
            frame_idx += 1
            
        cap.release()
        return extracted_paths, keyframes

    def analyze_style(self, video_path, user_instruction=""):
        """Analyzes video frames to extract color tone, contrast, aspect ratio, pacing, and visual style."""
        if not video_path or not os.path.exists(video_path):
            # Fallback analysis based purely on user instruction
            return {
                "aspect_ratio": "16:9",
                "dominant_colors": ["dark grey", "neon blue", "ambient yellow"],
                "brightness": "cinematic dark",
                "pacing": "moderate",
                "art_style": self.infer_style_from_prompt(user_instruction),
                "visual_cues": user_instruction
            }
            
        frame_paths, frames = self.extract_keyframes(video_path, num_frames=6)
        if not frames:
            return {
                "aspect_ratio": "16:9",
                "art_style": self.infer_style_from_prompt(user_instruction),
                "visual_cues": user_instruction
            }
            
        # 1. Aspect Ratio & Resolution
        height, width, _ = frames[0].shape
        ratio = f"{width}:{height}"
        aspect_str = "16:9" if width >= height else "9:16"
        
        # 2. Color Palette & Brightness Analysis
        avg_brightness = np.mean([np.mean(f) for f in frames])
        brightness_desc = "dark cinematic high-contrast" if avg_brightness < 100 else "vibrant well-lit clear"
        
        # Sample color analysis
        mean_colors = [np.mean(f, axis=(0, 1)) for f in frames] # BGR
        avg_bgr = np.mean(mean_colors, axis=0)
        
        color_desc = f"bgr({int(avg_bgr[0])}, {int(avg_bgr[1])}, {int(avg_bgr[2])})"
        
        # Infer style combining computer vision metrics and user instruction
        inferred_style = self.infer_style_from_prompt(user_instruction)
        
        return {
            "aspect_ratio": aspect_str,
            "width": width,
            "height": height,
            "brightness_level": float(avg_brightness),
            "brightness_desc": brightness_desc,
            "art_style": inferred_style,
            "visual_cues": f"{user_instruction} | Color tone: {color_desc} | {brightness_desc}",
            "keyframe_paths": frame_paths
        }

    def infer_style_from_prompt(self, instruction):
        inst_lower = instruction.lower()
        if "3d" in inst_lower or "render" in inst_lower or "unreal" in inst_lower:
            return "3D Render Cinematic, Octane engine lighting, volumetric mist"
        elif "cyberpunk" in inst_lower or "neon" in inst_lower or "future" in inst_lower:
            return "Cyberpunk dark neon synthwave aesthetic, reflective rain wet surfaces"
        elif "anime" in inst_lower or "illustration" in inst_lower or "drawing" in inst_lower:
            return "Modern digital anime illustration, clean cell shading, detailed linework"
        elif "documentary" in inst_lower or "real" in inst_lower or "realistic" in inst_lower:
            return "Photorealistic 8K documentary style, National Geographic cinematography, anamorphic lens"
        elif "minimalist" in inst_lower or "vector" in inst_lower or "flat" in inst_lower:
            return "Minimalist vector graphics, clean studio backdrop, high contrast geometry"
        else:
            return "Cinematic atmosphere, dark moody lighting, 8K ultra detail, photorealistic textures"
