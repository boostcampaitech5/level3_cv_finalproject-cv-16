import requests
import streamlit as st
from streamlit_cropper import st_cropper
from PIL import Image
import base64
import json
import io

st.set_option('deprecation.showfileUploaderEncoding', False)

# Upload an image and set some options for demo purposes
st.write("변환할 객체의 위치로 바운딩박스를 조절해주세요.")
img_file = st.sidebar.file_uploader(label='Upload a file', type=['png', 'jpg'])
realtime_update = st.sidebar.checkbox(label="Update in Real Time", value=True)
box_color = st.sidebar.color_picker(label="Box Color", value='#0000FF')
aspect_choice = st.sidebar.radio(label="Aspect Ratio", options=[
                                 "1:1"])
aspect_dict = {
    "1:1": (1, 1),
}
aspect_ratio = aspect_dict[aspect_choice]


def box_algorithm(img_file: Image, aspect_ratio: tuple = None) -> dict:
    box = (0, 0, 512, 512)
    height = 512
    width = 512
    return {'left': 0, 'top': 0, 'width': 512, 'height': 512}


if img_file:
    img = Image.open(img_file)
    if not realtime_update:
        st.write("Double click to save crop")
    # Get a cropped image from the frontend
    cropped_img = st_cropper(img, realtime_update=realtime_update, box_color=box_color,
                             aspect_ratio=aspect_ratio, box_algorithm=box_algorithm)

    # Manipulate cropped image at will
    st.write("Preview")
    _ = cropped_img.thumbnail((512, 512))
    st.image(cropped_img)
    print(cropped_img.size)
    # print(type(cropped_img))

    # byte 로 변환
    buffer = io.BytesIO()
    cropped_img.save(buffer, format='JPEG')
    buffer = buffer.getvalue()
    buffer = base64.b64encode(buffer)

    # submit button
    # Using the "with" syntax
    form = st.form(key='email')
    email = form.text_input('결과를 받을 이메일을 입력해주세요.')
    submit = form.form_submit_button('제출')

    print(type(email))
    # print(type(buffer.decode()))
    if submit:

        files = {"email": email, "image": buffer.decode()}
        response = requests.post(
            "http://127.0.0.1:8001/submit", data=json.dumps(files))

        st.write(f'10분내에 {email}로 결과가 전송됩니다.')
    else:
        st.write('제출 버튼을 눌러 애니메이션 변환 이미지를 받아보세요!')
