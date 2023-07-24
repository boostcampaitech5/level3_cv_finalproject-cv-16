import streamlit as st
from PIL import Image

def set_image_width(image_path, width):
    img_style = f"<style>img {{ max-width: {width}; }}</style>"
    st.markdown(img_style, unsafe_allow_html=True)
    st.image(image_path, use_column_width=True)
    
def centered_text(link_text, url):
    centered_style = "text-align: center;"
    st.write(f"<p style='{centered_style}'><a href='{url}'>{link_text}</a></p>", unsafe_allow_html=True)

def service_info():
    st.write("# 앗, 『이 세계』로부터의 손님이 내게 찾아왔다!?")
    st.write('---')

    img, _, text = st.columns([0.2, 0.02, 0.78])

    with img:
        new_width = int(main_img.width * 2)
        new_height = int(main_img.height * 2)
        resized_image = main_img.resize((new_width, new_height))
        st.image(resized_image)

    with text:
        st.write("## 사진 속에서 선택한 인물을 원하는 화풍을 묘사해 애니메이션화 하는 서비스")
        st.write('')
        st.write('##### 저희 서비스는 사용자들이 자신의 삶과 관심사를 연관시키는 창작물을 손쉽게 제작할 수 있도록 도와줍니다. 사용자들은 자신만의 독특한 사진을 만들고 공유하며, 창작에 어려움을 겪는 분들도 손쉽게 원하는 콘텐츠를 제작할 수 있습니다.')
        st.write('##### 특히 애니메이션과 웹툰을 좋아하는 분들이 쉽고 즐겁게 자신만의 창작물을 만들어 나가는 새로운 경험을 기대해 볼 수 있습니다.')

def service_example():
    st.text("")
    st.text("")
    st.text("")
    st.write('## Example')
    st.write('---')
    
    before, mid, after, a, b, c = st.columns(6)
    
    with before:
        st.image('image_video/main_cat.jpg', caption='Before', use_column_width=True)
        
    with mid:
        st.image('image_video/mid.png', use_column_width=True)
        
    with after:
        st.image('image_video/main_cat.jpg', caption='After', use_column_width=True)
        
def profile():
    st.text("")
    st.text("")
    st.text("")
    st.write('## Made By CV-16')
    images = st.columns([0.05, 0.18, 0.18, 0.18, 0.18, 0.18, 0.05])
    names = st.columns([0.05, 0.18, 0.18, 0.18, 0.18, 0.18, 0.05])
    
    with images[1]:
        set_image_width(profile_img, '100%')
        
    with images[2]:
        set_image_width(profile_img, '100%')
        
    with images[3]:
        set_image_width(profile_img, '100%')
        
    with images[4]:
        set_image_width(profile_img, '100%')

    with images[5]:
        set_image_width(profile_img, '100%')
        
    with names[1]:
        centered_text('T5065_김지현B', 'https://github.com/codehyunn')
        
    with names[2]:
        centered_text('T5082_박상필', 'https://github.com/SangphilPark')
        
    with names[3]:
        centered_text('T5124_오동혁', 'https://github.com/97DongHyeokOH')
        
    with names[4]:
        centered_text('T5141_이상민A', 'https://github.com/dldltkdals')

    with names[5]:
        centered_text('T5165_이태순', 'https://github.com/LTSGOD')

st.set_page_config(
    page_title="최『AI』",
    layout='wide',
)

main_img = Image.open('image_video/main_cat.jpg')
profile_img = Image.open('image_video/best_idol.jpg')

st.sidebar.info("Select a service above.")

service_info()
service_example()
profile()