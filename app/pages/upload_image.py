import requests
import streamlit as st
from streamlit_cropper import st_cropper
from PIL import Image
import base64
import json
import io
import re

with open('upload_image.css') as f :
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.set_option('deprecation.showfileUploaderEncoding', False)

# Upload an image and set some options for demo purposes
st.header("♥ 『이 세계』로부터 온 손님 보러가기 ♥")
img_file = st.sidebar.file_uploader(label='▶ 변환하고 싶은 파일을 올려주세요 ʕت̫͡ʔ', type=['png', 'jpg'])
realtime_update = st.sidebar.checkbox(label="Update in Real Time", value=True)
box_color = st.sidebar.color_picker(label="Box Color", value='#FF001A')
aspect_choice = st.sidebar.radio(label="Aspect Ratio", options=["1:1"])
aspect_dict = {"1:1": (1, 1)}
aspect_ratio = aspect_dict[aspect_choice]

def new_font_tag(text, mode) :
    if mode == 'title' :
        font = f"<p class='css-title-new-font'>{text}</p>"
    elif mode == 'content' :
        font = f"<p class='css-content-new-font'>{text}</p>" 
    st.markdown(font, unsafe_allow_html=True)
    
def box_algorithm(img_file: Image, aspect_ratio: tuple = None) -> dict:
    box = (0, 0, 512, 512)
    height = 512
    width = 512
    return {'left': 0, 'top': 0, 'width': 512, 'height': 512}

def check_size(img):
    w,h = img.size
    tmp = w if w > h else h

    if(tmp > 2024):
        ratio = 2024 / tmp
        img = img.resize((int(w * ratio), int(h * ratio)))
    return img

if img_file:
    new_font_tag("▼ 변환하고 싶은 인물에 최대한 가깝게 박스를 조절해주세요!", 'content')
    
    img = Image.open(img_file)
    img = img.convert('RGB')

    #이미지 size 가 1500 넘어갈 시 비율에 맞게 resize
    img = check_size(img)

    if not realtime_update:
        st.write("Double click to save crop")
    # Get a bbox coordinates from the frontend
    rect = st_cropper(img, return_type="box", realtime_update=realtime_update, box_color=box_color,
                      aspect_ratio=aspect_ratio, box_algorithm=box_algorithm)

    # bbox 좌표로부터 image crop
    cropped_img = img.crop(
        (rect['left'], rect['top'], rect['width'] + rect['left'], rect['height'] + rect['top']))

    # Manipulate cropped image at will
    new_font_tag("▼ 아래 사진에서 박스가 잘 지정됐는지 확인해보세요!", 'content')
    _ = cropped_img.thumbnail((512, 512))
    st.image(cropped_img)

    # byte 로 변환
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG')
    buffer = buffer.getvalue()
    buffer = base64.b64encode(buffer)

    # select character
    ver = ['최애의 아이','하울','명탐정 코난', '노진구', '홍시(홍시는 널 좋아해!)', 
            '단아(홍시는 널 좋아해!)', "메데이아(하루만 네가 되고 싶어)", "이아로스(하루만 네가 되고 싶어)"]

    form = st.form(key='email')
    selected = form.selectbox('변환하고 싶은 인물을 선택해주세요.', ver)
    email = form.text_input('결과를 받을 이메일을 입력해주세요.')
    submit = form.form_submit_button('제출')

    reg = "^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9]+\.[a-zA-Z]{2,3}$"

    if submit:
        if re.match(reg, email):
            files = {"email": email, "image": buffer.decode(),
                     "bbox": rect, "ver": selected}
            response = requests.post(
                "http://127.0.0.1:8001/submit", data=json.dumps(files))
            new_font_tag(f'10분 내에 {email}로 이 세계에서 온 손님이 찾아갑니다 ʕت̫͡ʔ', 'content')
        else:
            new_font_tag("유효한 메일 주소를 입력해주세요.", 'content')

    else:
        new_font_tag("제출 버튼을 눌러 이 세계에서 온 손님을 만나보세요 ʕت̫͡ʔ", 'content')
else:
    st.subheader('Guideline')
    st.write("바운딩 박스 지정시 <font color='blue'>사람 전체</font>가 선택될 수 있도록 지정해주세요!!!", unsafe_allow_html=True)
    
    st.image('image_video/o.png', caption="옳은 예시", use_column_width=True)
    
    st.image('image_video/x.jpg', caption="잘못된 예시", use_column_width=True)
