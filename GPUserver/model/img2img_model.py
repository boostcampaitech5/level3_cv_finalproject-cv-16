from diffusers import StableDiffusionImg2ImgPipeline

import numpy as np
import torch
import warnings
import PIL
import asyncio
# check_point_dump_path = "/opt/ml/Boostcamp-AI-Tech-Product-Serving/part3/01-fastapi/app/models/dump_paths/anythingn5-inpaint-anyv5"
check_point_dump_path = "/opt/ml/level3_cv_finalproject-cv-16/GPUserver/model/weights/dump_paths/corneos7th_heaven_mix_v2-anythingv3"
# weights/corneos7th_heaven_mix_v2-anythingv3
# lora_model = "./weights/Lora/add_detail.safetensors"
DEVICE = "cuda"

class StableDiffusionImg2Img():
    def __init__(self,check_point:str = check_point_dump_path):
        self.pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
            check_point,
            local_files_only=True,
            revision="fp16",
            torch_dtype=torch.float16
        )
        self.pipe.to(DEVICE)
        self.pipe.safety_checker = None
        self.pipe.requires_safety_checker = False
    def inpaint(self,prompt:str,negative_prompt:str,image:PIL.Image,num_inference_steps:str=100,strength:float=0.6)->PIL.Image:
        
        """
        image: 객체 이외의 배경을 제거한 이미지
        """
        while True:
            result = self.pipe(prompt = prompt,negative_prompt=negative_prompt,image=image,num_inference_steps=num_inference_steps, strength=strength).images[0]
            # 만약 result의 모든 픽셀이 검정 (0,0,0)이라면 inference 반복 
            if np.array(result).mean():
                break
        return result

    def load_Lora(self,lora_path:str):
        self.pipe.unet.load_attn_procs(lora_path)
if __name__ == "__main__":
    print("set")
    