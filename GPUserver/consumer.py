import os
import json
import time as pytime

import zlib
from base64 import b64encode, b64decode
import numpy as np
from redisqueue import RedisQueue
from google.cloud import storage
from PIL import Image
from io import BytesIO
from send_email import send_email
from model.inference_pipeline import Img2ImgWithBboxPipeline

# import bentoml
# from transform_anime import Transform_Anime

if __name__ == "__main__":

    # key 파일 열기
    with open("key.json") as f:
        key = json.load(f)

    # Redis Message Queue 접속
    q = RedisQueue('my-tae', host=key["REDIS_HOST"],
                   port=14914, password=key["REDIS_PASSWORD"])
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key["GOOGLE_APPLICATION_CREDENTIALS"]
    with open("model/weights/diffusion/Lora/prompt.json") as Lora:
        Lora= json.load(Lora)
    model = Img2ImgWithBboxPipeline()
    
    # message get
    while(True):
        msg = q.get(isBlocking=True)  # 큐가 비어있을 때 대기
        if msg is not None:
            msg_json = json.loads(msg.decode('utf-8'))
            print(msg_json)
            pytime.sleep(3)  # 결과를 천천히 보기 위해 3 seconds sleep

        id = msg_json['id']
        email = msg_json['email']
        bbox = msg_json['bbox']
        ver = msg_json['ver']

        bucket_name = key["BUCKET_NAME"]    # 서비스 계정 생성한 bucket 이름 입력
        source_blob_name = f'{id}.jpg'    # GCP에 저장되어 있는 파일 명
        # 다운받을 파일을 저장할 경로("local/path/to/file")
        destination_file_name = f'{id}.jpg'

        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(source_blob_name)

        # 압축파일 원상 복구
        text = blob.download_as_string()

        uncompressed_img = zlib.decompress(text)
        decoded_data = b64decode(uncompressed_img)
        img = Image.open(BytesIO(decoded_data))

        # bbox 기반 image crop
        x1,y1,x2,y2 = bbox['left'], bbox['top'], bbox['width'] +bbox['left'], bbox['height'] + bbox['top']
        cropped_img = img.crop((x1,y1,x2,y2)).resize((512, 512))
        input_bbox = np.array([x1,y1,x2,y2])
        
        # ------------------------model inference ----------------------------
        # Loading Lora

        character,prompt = Lora[ver]["character"],Lora[ver]["prompt"]
        lora_path = f"model/weights/diffusion/Lora/{character}/checkpoint-400"
        model.load_lora(lora_path)
        result = model.pipe(image=img,input_bbox=input_bbox,prompt=prompt)
        
        # Bentoml
        # model 변경점은 이 코드 위에서 수정해주세요
        # bento_service = Transform_Anime()
        # bento_service.pack('model', model)
        
        # result = bento_service.transform(image=img,input_bbox=input_bbox,prompt=prompt)
        # ------------------------model inference ----------------------------

        send_email(email, result)
