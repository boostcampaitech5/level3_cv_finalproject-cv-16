import streamlit as st

# 로컬 동영상 파일 경로
video_path = "../image_video/how_to_use.mp4"

# 동영상 표시
st.write('## 사용 방법')
st.write('---')
st.video(video_path)