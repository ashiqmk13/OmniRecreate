import os
import subprocess
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from config import TEMP_DIR, DEVICE, FACELESS_POSITIVE_PROMPT, FACELESS_NEGATIVE_PROMPT

class VisualGenerator:
    def __init__(self, mode="auto"):
        self.mode = mode
        self._diffusers_pipe = None

    def _init_sdxl_lightning(self):
        """Initializes SDXL Lightning / SD 1.5 pipeline if PyTorch GPU is active."""
        if self._diffusers_pipe is None and DEVICE == "cuda":
            try:
                from diffusers import StableDiffusionXLPipeline, EulerDiscreteScheduler
                model_id = "ByteDance/SDXL-Lightning"
                self._diffusers_pipe = StableDiffusionXLPipeline.from_pretrained(
                    model_id,
                    torch_dtype=torch.float16,
                    variant="fp16"
                ).to("cuda")
                self._diffusers_pipe.scheduler = EulerDiscreteScheduler.from_config(
                    self._diffusers_pipe.scheduler.config, timestep_spacing="trailing"
                )
            except Exception as e:
                print(f"Diffusers GPU load note: {e}. Utilizing fast canvas engine.")
                self._diffusers_pipe = "procedural"

    def generate_scene_visual(
        self,
        visual_prompt,
        duration_seconds=5.0,
        scene_id=1,
        lock_facial_features=True,
        character_reference_image=None,
        aspect_ratio="16:9"
    ):
        """
        Generates visual video clip for a single scene.
        Returns: absolute path to generated .mp4 clip file.
        """
        output_clip_path = os.path.join(TEMP_DIR, f"visual_scene_{scene_id:03d}.mp4")
        
        # Enforce facial lock / unlock
        final_prompt = visual_prompt
        neg_prompt = ""
        if lock_facial_features:
            final_prompt += f", {FACELESS_POSITIVE_PROMPT}"
            neg_prompt = FACELESS_NEGATIVE_PROMPT
        else:
            final_prompt += ", detailed facial features, character expressive portrait"

        if character_reference_image and os.path.exists(character_reference_image):
            final_prompt += " matching input character reference visual style and outfit"

        # Width and height
        if aspect_ratio == "9:16":
            width, height = 720, 1280
        else:
            width, height = 1280, 720

        # Generate image frame
        img_path = self._generate_image_frame(final_prompt, neg_prompt, width, height, scene_id)

        # Convert image to animated video clip with subtle motion / zoom pan (Ken Burns effect)
        self._convert_image_to_animated_clip(img_path, output_clip_path, duration_seconds, width, height)

        return output_clip_path

    def _generate_image_frame(self, prompt, neg_prompt, width, height, scene_id):
        """Generates frame image using AI or procedural engine."""
        img_path = os.path.join(TEMP_DIR, f"frame_scene_{scene_id:03d}.jpg")
        
        if DEVICE == "cuda":
            try:
                self._init_sdxl_lightning()
                if hasattr(self._diffusers_pipe, "__call__"):
                    image = self._diffusers_pipe(
                        prompt,
                        negative_prompt=neg_prompt,
                        num_inference_steps=4,
                        guidance_scale=0.0
                    ).images[0]
                    image.save(img_path)
                    return img_path
            except Exception as e:
                print(f"Diffusers generation notice: {e}")

        # High Quality Procedural Canvas Fallback Generator
        return self._generate_procedural_art_frame(prompt, width, height, img_path, scene_id)

    def _generate_procedural_art_frame(self, prompt, width, height, output_path, scene_id):
        """Creates high-end stylized background visuals with atmospheric lighting & faceless silhouettes."""
        img = Image.new("RGB", (width, height), color=(15, 18, 25))
        draw = ImageDraw.Draw(img)

        # 1. Gradient atmospheric background
        c1 = (int(10 + (scene_id * 15) % 40), int(20 + (scene_id * 25) % 50), int(40 + (scene_id * 35) % 80))
        c2 = (int(5 + (scene_id * 10) % 20), int(8 + (scene_id * 12) % 25), int(15 + (scene_id * 20) % 40))
        
        for y in range(height):
            r = int(c1[0] + (c2[0] - c1[0]) * (y / height))
            g = int(c1[1] + (c2[1] - c1[1]) * (y / height))
            b = int(c1[2] + (c2[2] - c1[2]) * (y / height))
            draw.line([(0, y), (width, y)], fill=(r, g, b))

        # 2. Glowing tech geometry / grid
        grid_color = (int(c1[0]*1.5), int(c1[1]*2.0), int(c1[2]*2.2))
        for x in range(0, width, 80):
            draw.line([(x, 0), (x, height)], fill=grid_color, width=1)
        for y in range(0, height, 80):
            draw.line([(0, y), (width, y)], fill=grid_color, width=1)

        # 3. Faceless mannequin silhouette / character representation
        center_x = width // 2
        center_y = height // 2 + 50
        
        # Glow orb behind head
        draw.ellipse(
            [center_x - 120, center_y - 220, center_x + 120, center_y + 20],
            fill=(int(c1[0]*2.5), int(c1[1]*3.0), int(c1[2]*3.2))
        )
        
        # Faceless Head (smooth oval with zero facial features)
        draw.ellipse(
            [center_x - 45, center_y - 180, center_x + 45, center_y - 80],
            fill=(230, 235, 245), outline=(100, 110, 130), width=2
        )
        
        # Body Silhouette
        draw.polygon(
            [(center_x - 70, center_y - 75), (center_x + 70, center_y - 75),
             (center_x + 110, center_y + 180), (center_x - 110, center_y + 180)],
            fill=(25, 30, 42)
        )

        # Soft blur vignette effect
        img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
        img.save(output_path, quality=95)
        return output_path

    def _convert_image_to_animated_clip(self, img_path, output_mp4, duration_seconds, width, height):
        """Converts static image into animated video clip with slow cinematic zoom."""
        fps = 24
        total_frames = int(duration_seconds * fps)
        
        cmd = [
            "ffmpeg", "-y", "-loop", "1", "-i", img_path,
            "-vf", f"zoompan=z='min(zoom+0.0015,1.15)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={width}x{height}",
            "-c:v", "libx264", "-t", str(duration_seconds), "-pix_fmt", "yuv420p",
            output_mp4
        ]
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if not os.path.exists(output_mp4):
            # Simple freeze-frame video fallback
            cmd_simple = [
                "ffmpeg", "-y", "-loop", "1", "-i", img_path,
                "-c:v", "libx264", "-t", str(duration_seconds), "-pix_fmt", "yuv420p",
                "-s", f"{width}x{height}", output_mp4
            ]
            subprocess.run(cmd_simple, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
