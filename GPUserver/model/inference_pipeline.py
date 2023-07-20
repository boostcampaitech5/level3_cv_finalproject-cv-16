from model.inpaint_model import  StableDiffusionInpaint
from model.img2img_model import StableDiffusionImg2Img
from model.segment_anything_model import SAM
from PIL import Image
import numpy as np 
from typing import Optional
from model.utils import image_resize,image_segmentation,combine_image

class inpaint_with_bbox_Pipeline():

    def __init__(self):
        self.inpaintor = StableDiffusionInpaint()
        # self.inpaintor.load_lora()

        self.segmentation = SAM()
    

    
    def pipe(self,image:Image.Image,input_bbox:np.array,prompt:str,inference_steps:int=200,mask:Optional[Image.Image]=None):
        
        #만약 파라미터에 mask 객체가 없다면 mask를 만듦
        if not mask:
            mask = self.segmentation.make_mask_with_bbox(image,input_bbox)
        result = self.inpaintor.inpaint(image,mask,prompt,inference_steps)

        return result

check_point_dump_path = "/opt/ml/level3_cv_finalproject-cv-16/GPUserver/model/weights/dump_paths/corneos7th_heaven_mix_v2-anythingv3"
class Img2ImgWithBboxPipeline():

    def __init__(self,check_point:str=check_point_dump_path):

        self.image_translation = StableDiffusionImg2Img(check_point = check_point)
        self.segmentation = SAM()
        #객체를 제거해줄 inpainting 모델
        self.inpaintor = inpaint_with_bbox_Pipeline()
    def load_lora(self,check_point:str):
        self.image_translation.load_Lora(check_point)
    def pipe(self,image:Image.Image,input_bbox:np.array,prompt:str,inference_steps:int=100,strength:float=0.6)->Image.Image:
        #1.입력 이미지에서 마스크 추출
        mask = self.segmentation.make_mask_with_bbox(image,input_bbox)
        """
        1번을 수행한다면 아래 2번과 3번 과정은 비동기로 작성해도 가능할 것 같다.
        추후 속도를 위해 개선할 예정!
        """
        #2-1. 위에서 추출된 마스크 이외의 배경을 제거한 뒤, 이미지 변환
        segment_img = image_segmentation(image,mask)

        target_image = self.image_translation.inpaint(prompt=prompt,image=segment_img,num_inference_steps=inference_steps,strength=strength)
   
        #3. 이미지에서 1번에서 추출한 객체를 inpaint를 사용하여 자연스럽게 제거
        # background = self.inpaintor.pipe(image=image,input_bbox=None,prompt="",inference_steps=100,mask=mask)

        background = image 
        #3.1, 3번의 결과로 512,512사이즈의 배경이미지가 반환되기 때문에 원본 사이즈에 맞춰 늘려주는 과정
        background = image_resize(image=target_image,background=background)

        target_mask = self.segment_image(image = target_image,input_bbox=input_bbox)
        #4 이미지를 합치기 전에 target_image의 mask를 통해 배경과 객체를 분리
        target_image,target_background = image_segmentation(image=target_image,mask=target_mask,background=background)  
        #5. 4번 과정에서 얻은 결과를 통해 두이미지를 합친다.
        result = combine_image(background=target_background,image=target_image)
        return result
    
    #좌표의 위치에 대한 segmetation을 수행하는 함수
    def segment_image(self,image:Image.Image,ßinput_bbox:np.array) -> Image.Image:
        mask = self.segmentation.make_mask_with_bbox(image,input_bbox)
        return mask

    
        