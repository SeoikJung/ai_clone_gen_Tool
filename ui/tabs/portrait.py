import json
import os
import uuid
from datetime import datetime
import random
import torch
from diffusers import StableDiffusionXLPipeline
from PIL import Image
import torch

torch.cuda.empty_cache()
class PortraitGenerator:
    def __init__(self, model_path="models/RealVisXL_V4.0", device="cuda"):
        self.model_path = model_path
        self.device = device
        self.pipeline = StableDiffusionXLPipeline.from_pretrained(
            model_path,
            torch_dtype=torch.float16,
            variant="fp16",
            use_safetensors=True
        ).to(device)
        self.settings = {
            "model_path": model_path,
            "prompt": "beautiful lady, (freckles), big smile, brown hazel eyes, Short hair, rainbow color hair, dark makeup, hyperdetailed photography, soft light, head and shoulders portrait, cover",
            "negative_prompt": "bad eyes, cgi, airbrushed, plastic, watermark",
            "width": 832,
            "height": 1216,
            "cfg": 8,
            "steps": 40,
            "strength": 0.35,
            "seed": None,
            "timestamp": None,
            "file_path": None,
            "unique_id": None
        }

    def set_settings(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.settings:
                self.settings[key] = value

    def generate(self):
        torch.backends.cuda.matmul.allow_tf32 = True
        now = datetime.now().strftime("%Y-%m-%d")
        output_dir = f"result/portrait/{now}"
        unique_id = uuid.uuid4()
        os.makedirs(output_dir, exist_ok=True)

        # 시드 설정
        if self.settings["seed"] is None:
            self.settings["seed"] = random.randint(0, 2**32 - 1)
        self.settings["timestamp"] = now
        self.settings["unique_id"] = str(unique_id)

        generator = torch.manual_seed(self.settings["seed"])

        # 이미지 생성
        image = self.pipeline(
            prompt=self.settings["prompt"],
            negative_prompt=self.settings["negative_prompt"],
            width=self.settings["width"],
            height=self.settings["height"],
            guidance_scale=self.settings["cfg"],
            num_inference_steps=self.settings["steps"],
            generator=generator,
            strength=self.settings["strength"]
        ).images[0]

        # 이미지 저장
        file_path = os.path.join(output_dir, f"{unique_id}.png")
        image.save(file_path)
        torch.cuda.empty_cache()

        self.settings["file_path"] = file_path
        # 설정과 로그를 함께 저장
        self.save_settings_and_log(output_dir, unique_id)
        
        return image , file_path

    def save_settings_and_log(self, output_dir, unique_id):
        log_file = os.path.join(output_dir, f"{unique_id}.json")
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=4)

    def load_settings(self, filename="settings.json"):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                self.settings = json.load(f)
        except FileNotFoundError:
            print(f"Error: {filename} not found")