from model.img2img_model import StableDiffusionImg2Img
from model.segment_anything_model import SAM
from PIL import Image,ImageChops
import numpy as np 
from model.utils import image_resize,image_segmentation,combine_image, check_size, mask_composit, mask_composit2
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
        #1. 입력 이미지에서 마스크 추출
        mask = self.segmentation.make_mask_with_bbox(image,input_bbox)
        """
        1번을 수행한다면 아래 2번과 3번 과정은 비동기로 작성해도 가능할 것 같다.
        추후 속도를 위해 개선할 예정!
        """
        #2-1. 위에서 추출된 마스크 이외의 배경을 제거
        segment_img = image_segmentation(image,mask)


        #2-2. 선택된 객체만 crop
        crop_img = segment_img.crop((input_bbox[0],input_bbox[1],input_bbox[2],input_bbox[3]))

        #2-3. 선택된 객체 resize
        resized_crop_img = check_size(crop_img)

        #3. Resize한 객체 캐릭터 생성
        resized_target_image = self.image_translation.inpaint(prompt=prompt,negative_prompt=negative_prompt,image=resized_crop_img,num_inference_steps=inference_steps,strength=strength)

        #3-1. 크기 Resize한 객체 원본 크기로 돌리기
        x = input_bbox[2] - input_bbox[0]
        y = input_bbox[3] - input_bbox[1]
        target_image = resized_target_image.resize((x, y),Image.ANTIALIAS)

        #4. 캐릭터 마스크 재생성
        x, y = target_image.size
        bbox = np.array([0,0,x,y])

        crop_mask = self.segmentation.make_mask_with_bbox(target_image, bbox)
        # SAM에서 마스크의 테두리 부분이 잘 Seg 되지 않는 현상 때문에 미세하게 crop 진행
        crop_mask = crop_mask.crop((4,4,x-4,y-4))

        # 마스크 반전
        crop_mask = ImageChops.invert(crop_mask)

        #5. 애니 생성 후 원본 이미지 크기의 마스크 만들기
        after_mask = mask_composit(image=image,crop_img=crop_mask, input_bbox=input_bbox)

        #6. 위에서 추출된 마스크 이외의 배경 제거
        after_segment_img = mask_composit2(image, target_image, input_bbox)

        #7. 원본 배경만 남기기
        background = self.outpaint(image,mask,15)

        #8. 이미지를 합치기 전에 target_image의 mask를 통해 배경과 객체를 분리
        target_image,target_background = image_segmentation(image=after_segment_img,mask=after_mask,background=background)  
        
        #9. 8번 과정에서 얻은 결과를 통해 두이미지를 합친다.
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

    
        