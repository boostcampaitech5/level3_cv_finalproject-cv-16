from PIL import Image
import numpy as np
from typing import Optional

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

def check_size(img):
    w,h = img.size
    tmp = w if w > h else h
    standard = 950

    ratio = standard / tmp
    img = img.resize((int(w * ratio), int(h * ratio)),Image.ANTIALIAS)
    return img

def mask_composit(image:Image.Image,crop_img:Image.Image,input_bbox:np.array)->Image.Image:
    x,y = image.size
    board = np.zeros((y,x),dtype=bool)
    board[input_bbox[1]+4:input_bbox[3]-4, input_bbox[0]+4:input_bbox[2]-4] = np.array(crop_img)

    board = Image.fromarray(board)
    return board

def mask_composit2(image:Image.Image,orig_img:Image.Image,input_bbox:np.array)->Image.Image:
    x,y = image.size
    board = np.zeros((y,x,3),dtype=np.uint8)
    board[input_bbox[1]:input_bbox[3], input_bbox[0]:input_bbox[2]] = np.array(orig_img)
    board = Image.fromarray(board)

    return board