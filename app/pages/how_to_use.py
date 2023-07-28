import streamlit as st

with open('how_to_use.css') as f :
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
# 로컬 동영상 파일 경로
video_path = "image_video/how_to_use.mp4"

# 동영상 표시
st.write('## ♥ 사용 방법 ♥')
st.write('---')
st.video(video_path)

# 영상 위에 사진으로 설명 추가하면 더 좋을듯