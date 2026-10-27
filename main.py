import streamlit as st
st.title('나의 첫 웹 서비스 만들기')
st.textinput('이름을 입력하세요')
st.selectbox('좋아하는 음식을 선택하세요',['마라탕','고바순','마왕족발'])
st.button('인사말 생성')
