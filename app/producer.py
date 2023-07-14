import json

import zlib
from base64 import b64encode, b64decode

from redisqueue import RedisQueue
from google.cloud import storage

import io
import os
from PIL import Image


def producer(file):

    # key.yaml 불러오기
    with open('key.json', 'r') as f:
        key = json.load(f)

    q = RedisQueue('my-tae', host=key['REDIS_HOST'],
                   port=14914, password=key['REDIS_PASSWORD'])

    # encoded_img = b64encode()
    # compressed_img = zlib.compress(encoded_img, 9)

    # GCS 인증
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key['GOOGLE_APPLICATION_CREDENTIALS']

    bucket_name = key["BUCKET_NAME"]
    destination_blob_name = f'img_{file.id}.jpg'

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    # encode image 복구
    decode_buffer = b64decode(file.image)
    image_buffer = io.BytesIO(decode_buffer)
    image = Image.open(image_buffer)

    # 이미지 저장 -> GCS 버킷에 저장하기 위해
    image.save(f'{file.id}.jpg')
    source_path = f'{file.id}.jpg'

    blob.upload_from_filename(source_path)

    # 이미지 삭제 -> 추후 주기적으로 삭제하는식으로 바꿔도 될듯
    os.remove(f'{file.id}.jpg')

    message = dict()
    message['id'] = str(file.id)
    message_str = json.dumps(message)
    q.put(message_str)
