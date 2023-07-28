from PIL import Image
import numpy as np
from typing import Optional
#원본 이미지에서 crop할 좌표를 반환해주는 함수
def crop_coord(image:Image.Image,bbox:np.array):
    w,h = image.size
    x1,y1,x2,y2 = bbox
    mid_x,mid_y = int((x1+x2)/2),int((y1+y2)/2)
    bbox_area = abs(x2-x1)*abs(y2-y1)
    #length: crop할 이미지의 한변의 길이
    length = int((bbox_area*10/3)**(1/2))

    # x1,y1,x2,y2 = mid_x-length//2,mid_y-length//2,mid_x+length//2,mid_y+length//2
    # if x1 < 0:
    #     x2 = abs(x1)+ x2
    #     x1 = 0
    # elif x2 > w:
    #     x1 -= abs((x2 - w))
    #     x2 = w-1
    # elif y1 < 0:
    #     y2 = abs(y1)+ y2
    #     y1 = 0
    # elif y2 > h:
    #     y1 -= abs((y2 - h))
    #     y2 = h-1
    nx1 = max(0, mid_x - length // 2)
    nx2 = min(w, mid_x + length // 2)
    ny1 = max(0, mid_y - length // 2)
    ny2 = min(h, mid_y + length // 2)
    return nx1,ny1,nx2,ny2,np.array([x1-nx1,y1-ny1,x2-nx1,y2-ny1])
def img_padding(image:Image.Image,target_image:Image.Image,coord) -> Image.Image:
    x1,y1,x2,y2 = coord
    w,h = image.size
    target_image = np.array(target_image)
    zero_array = np.zeros((w,h,3))
    zero_array[y1:y1+h,x1:x1+w,:] = target_image
    target_image = Image.fromarray(zero_array)
    return target_image
# 원본 이미지 대비 사용자로 부터 입력받은 bbox의 크기를 체크하여 crop할지 판단
def check_crop_inference(image:Image.Image,bbox_area:int) -> bool:
    w,h  = image.size
    img_area = w*h
    bbox_per_image = bbox_area/img_area
    if bbox_per_image <= 0.30:
        return True
    else:
        return False
    
def image_segmentation(image:Image.Image,mask:Image.Image,background:Optional[Image.Image] = None):
    """
    image: 원본 이미지
    mask: 선택된 객체의 마스크
    target_image: 원본이미지에서 mask 이외 영역이 제거된 이미지
    background: inpainting을 통해 객체가 제거된 배경이미지
    """
    input_image = np.array(image)
    input_mask = np.array(mask).astype(np.uint8)
    reversed_mask = np.where(input_mask == 0, 1, 0)
   
    #mask와 image의 채널을 맞추는 과정
    input_mask = np.repeat(input_mask[..., np.newaxis], 3, -1)
    reversed_mask = np.repeat(reversed_mask[..., np.newaxis], 3, -1).astype(np.uint8) 
    
    #input_image에 input_mask를 곱해 mask이외 배경을 제거하는 과정
    target_image = input_image * input_mask
    target_image = Image.fromarray(target_image)

    if background:
        # background = image_resize(image)
        target_background = background*reversed_mask
        target_background = Image.fromarray(target_background)
        return target_image,target_background
    else:
        return target_image
def image_resize(image:Image.Image,background:Image.Image) -> Image.Image:
    w,h = image.size
    background = background.resize((w,h),Image.LANCZOS)
    return background
def combine_image(background:Image.Image,image:Image.Image) -> Image.Image:
    background,image = np.array(background), np.array(image)
    result_np = background+image
    result_pil = Image.fromarray(result_np)
    return result_pil