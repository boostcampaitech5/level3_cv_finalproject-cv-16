from diffusers import StableDiffusionInpaintPipeline
import torch
from PIL import Image
import numpy as np


check_point_dump_path = "/opt/ml/level3_cv_finalproject-cv-16/GPUserver/model/weights/dump_paths/corneos7th_heaven_mix_v2-anythingv3"
# lora_model = "weights/Lora/add_detail.safetensors"
DEVICE = "cuda"

class StableDiffusionInpaint():
    def __init__(self,check_point:str=check_point_dump_path):

        self.pipe = StableDiffusionInpaintPipeline.from_pretrained(
            check_point,
            local_files_only=True,
            revision="fp16",

            torch_dtype = torch.float16)
        self.pipe.to(DEVICE)
        self.pipe.safety_checker = None
        self.pipe.requires_safety_checker = False

    def inpaint(self,image:Image,mask: Image,prompt:str,inference_steps:int=200) -> Image:
      

        output = self.pipe(
        prompt = prompt,
        image = image,
        mask_image = mask,
        num_inference_steps= inference_steps).images[0]

        return output

    def load_lora(self,lora_path:str):
        self.pipe.load_lora_weights(lora_path)

if __name__ == "__main__":
    StableDiffusionInpaint()
    print("complete")