import streamlit as st
st.title('나의 첫 웹 서비스 만들기')
a=st.text_input('이름을 입력하세요')
b=st.selectbox('좋아하는 음식을 선택하세요',['마라탕','고바순','마왕족발','치미창가','초코바게트','한정선','치즈크러스트 피자','스테이크','대게','보일링씨푸드','생새우'])
if st.button('인사말 생성'):
  st.write('반갑습니다')
