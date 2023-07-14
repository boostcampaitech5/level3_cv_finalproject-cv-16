from fastapi import FastAPI, UploadFile, File
from fastapi.param_functions import Depends
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from typing import List, Union, Optional, Dict, Any

from datetime import datetime
from producer import producer

app = FastAPI()


class resized_img(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    # user_name - > 아이디 로그인 구현되면
    email: str
    image: bytes


@app.post("/submit", description="image submit button")
def submit(file: resized_img) -> bool:
    print(file.id, file.email, type(file.image))
    producer(file)
    return True

# ToDo
# 이미지를 전체이미지도 알아야하고 crop 된것도 보내야하는거아닌가
