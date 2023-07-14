### 서버 실행 순서

1. [GCS에서 버킷 만들기](https://soundprovider.tistory.com/entry/GCP-Python%EC%97%90%EC%84%9C-GCP-Cloud-Storage-%EC%97%B0%EB%8F%99%ED%95%98%EA%B8%B0)
2. [redislab 접속해서 redis-server cloud 만들기](https://inpa.tistory.com/entry/REDIS-%F0%9F%93%9A-Redis%EB%A5%BC-%ED%81%B4%EB%9D%BC%EC%9A%B0%EB%93%9C%EB%A1%9C-%EC%82%AC%EC%9A%A9%ED%95%98%EC%9E%90-Redislabs?category=918728)
3. key.json 파일 만들고 설정
```
{
    "GOOGLE_APPLICATION_CREDENTIALS" : "JSON 경로"
    "REDIS_HOST":"REDIS IP주소",
    "REDIS_PASSWORD" : "REDIS API 키"
}
```
4. 터미널에서 streamlit 실행
```
streamlit run frontend.py   
```
5. 터미널에서 fastapi backend 실행
```
python __main__.py
```

### 구현 내용
- 프론트에서 이미지 받아서 gcs 에 crop 이미지 저장하고 redis message queue에 이미지 고유 id push 까지 구현
