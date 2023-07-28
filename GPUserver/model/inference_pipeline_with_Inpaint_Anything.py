from model.img2img_model import StableDiffusionImg2Img
from model.segment_anything_model import SAM
from PIL import Image
import numpy as np 
from model.utils import image_resize,image_segmentation,combine_image, check_crop_inference,crop_coord,img_padding
from model.Inpaint_Anything.lama_inpaint import inpaint_img_with_lama
from model.Inpaint_Anything.utils import save_array_to_img, dilate_mask


LAMA_CONFIG = 'model/Inpaint_Anything/lama/configs/prediction/default.yaml'
LAMA_MODEL = 'model/Inpaint_Anything/pretrained_models/big-lama'
check_point_dump_path = "/opt/ml/level3_cv_finalproject-cv-16/GPUserver/model/weights/dump_paths/corneos7th_heaven_mix_v2-anythingv3"
class Img2ImgWithBboxPipeline():

    def __init__(self,check_point:str=check_point_dump_path):

        self.image_translation = StableDiffusionImg2Img(check_point = check_point)
        self.segmentation = SAM()
    def load_lora(self,check_point:str):
        self.image_translation.load_Lora(check_point)
    def pipe(self,image:Image.Image,input_bbox:np.array,prompt:str,negative_prompt:str,inference_steps:int=100,strength:float=0.6)->Image.Image:
        #1.입력 이미지에서 마스크 추출
        bbox_area = (input_bbox[2]-input_bbox[0])*(input_bbox[3]-input_bbox[1])
        mask = self.segmentation.make_mask_with_bbox(image,input_bbox)
        
        # crop을 할지 체크하는 함수
        if check_crop_inference(image=image,bbox_area=bbox_area):
            x1,y1,x2,y2,input_bbox = crop_coord(image=image,bbox=input_bbox)
            cropped_img = image.crop((x1,y1,x2,y2))
            cropped_mask = mask.crop((x1,y1,x2,y2))
            segment_img = image_segmentation(cropped_img,cropped_mask)

            target_image = self.image_translation.inpaint(prompt=prompt,negative_prompt=negative_prompt,image=segment_img,num_inference_steps=inference_steps,strength=strength)
    
            background = self.outpaint(image,mask,15)
            target_image = img_padding(image=image,target_image=target_image,coord = (x1,y1,x2,y2))

            target_mask = self.segment_image(image = target_image,input_bbox=input_bbox)
            
            #4 이미지를 합치기 전에 target_image의 mask를 통해 배경과 객체를 분리
            target_image,target_background = image_segmentation(image=target_image,mask=target_mask,background=background)  
            #5. 4번 과정에서 얻은 결과를 통해 두이미지를 합친다.
            result = combine_image(background=target_background,image=target_image)
        else:
            
            """
            1번을 수행한다면 아래 2번과 3번 과정은 비동기로 작성해도 가능할 것 같다.
            추후 속도를 위해 개선할 예정!
            """
        
            #2-1. 위에서 추출된 마스크 이외의 배경을 제거한 뒤, 이미지 변환
            segment_img = image_segmentation(image,mask)

            target_image = self.image_translation.inpaint(prompt=prompt,negative_prompt=negative_prompt,image=segment_img,num_inference_steps=inference_steps,strength=strength)
    
            background = self.outpaint(image,mask,15)
            background = image_resize(image=target_image,background=background)

            target_mask = self.segment_image(image = target_image,input_bbox=input_bbox)
            #4 이미지를 합치기 전에 target_image의 mask를 통해 배경과 객체를 분리
            target_image,target_background = image_segmentation(image=target_image,mask=target_mask,background=background)  
            #5. 4번 과정에서 얻은 결과를 통해 두이미지를 합친다.
            result = combine_image(background=target_background,image=target_image)
        return result
    
    def outpaint(self,image:Image.Image,mask:Image.Image,dilate_kernel_size:int) -> Image.Image:
        mask = np.array(mask)
        mask = dilate_mask(np.array(mask),dilate_kernel_size)
        background = Image.fromarray(inpaint_img_with_lama(
    np.array(image), mask, LAMA_CONFIG, LAMA_MODEL, device="cuda"))
        return background
    #좌표의 위치에 대한 segmetation을 수행하는 함수
    def segment_image(self,image:Image.Image,input_bbox:np.array) -> Image.Image:
        mask = self.segmentation.make_mask_with_bbox(image,input_bbox)
        return mask

    
        