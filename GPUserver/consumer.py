import os
import json
import time as pytime

import zlib
from base64 import b64encode, b64decode

from redisqueue import RedisQueue
from google.cloud import storage
from send_email import send_email

if __name__ == "__main__":
    with open("key.json") as f:
        key = json.load(f)
    q = RedisQueue('my-tae', host=key["REDIS_HOST"],
                   port=14914, password=key["REIDS_PASSWORD"])
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key["GOOGLE_APPLICATION_CREDENTIALS"]

    # message get
    while(True):
        msg = q.get(isBlocking=True)  # 큐가 비어있을 때 대기
        if msg is not None:
            msg_json = json.loads(msg.decode('utf-8'))
            print(msg_json)
            pytime.sleep(3)  # 결과를 천천히 보기 위해 3 seconds sleep

        id = msg_json['id']
        email = msg_json['email']

        bucket_name = key["BUCKET_NAME"]    # 서비스 계정 생성한 bucket 이름 입력
        source_blob_name = f'{id}.jpg'    # GCP에 저장되어 있는 파일 명
        # 다운받을 파일을 저장할 경로("local/path/to/file")
        destination_file_name = f'{id}.jpg'

        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(source_blob_name)

        blob.download_to_filename(destination_file_name)

        # ------------------------model inference ----------------------------

        send_email(email, id)
