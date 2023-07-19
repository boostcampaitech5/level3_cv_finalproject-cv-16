import json

import zlib
from base64 import b64encode, b64decode

from google.cloud import storage

import io
import os
from PIL import Image


import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from GPUserver.redisqueue import RedisQueue

def producer(file):

    # key.yaml 불러오기
    with open('key.json', 'r') as f:
        key = json.load(f)

    q = RedisQueue('my-tae', host=key['REDIS_HOST'],
                   port=14914, password=key['REDIS_PASSWORD'])

    # GCS 인증
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key['GOOGLE_APPLICATION_CREDENTIALS']

    bucket_name = key["BUCKET_NAME"]
    destination_blob_name = f'{file.id}.jpg'

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    # 이미지 압축
    compressed_img = zlib.compress(file.image, 9)

    # GCS에 압축 이미지 업로드
    blob.upload_from_string(compressed_img)

    # Message Queue에 전달할 message setting
    message = dict()
    message['id'] = str(file.id)
    message['email'] = file.email
    message['bbox'] = file.bbox
    message['ver'] = file.ver
    message_str = json.dumps(message)
    q.put(message_str)
