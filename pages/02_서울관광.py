
import streamlit as st
import folium
from streamlit_folium import st_folium

# 페이지 설정
st.set_page_config(
    page_title="서울 관광지 TOP 10",
    page_icon="🗺️",
    layout="wide"
)

# 제목
st.title("🗺️ 외국인이 좋아하는 서울 관광지 TOP 10")
st.write("서울의 대표 관광지를 지도에서 확인해 보세요!")

# 관광지 데이터
spots = [
    {
        "name": "경복궁",
        "lat": 37.5796,
        "lon": 126.9770,
        "category": "역사·문화",
        "desc": "조선 왕조의 대표 궁궐입니다. 근정전과 경회루 등 아름다운 전통 건축물을 볼 수 있습니다."
    },
    {
        "name": "N서울타워",
        "lat": 37.5512,
        "lon": 126.9882,
        "category": "전망·야경",
        "desc": "남산 정상에 있는 전망 명소입니다. 서울의 아름다운 전경과 야경을 감상할 수 있습니다."
    },
    {
        "name": "명동",
        "lat": 37.5636,
        "lon": 126.9869,
        "category": "쇼핑·먹거리",
        "desc": "화장품과 패션 매장, 다양한 길거리 음식이 모여 있는 서울의 대표 쇼핑 거리입니다."
    },
    {
        "name": "북촌한옥마을",
        "lat": 37.5826,
        "lon": 126.9830,
        "category": "전통·거리",
        "desc": "전통 한옥이 모여 있는 아름다운 마을로 한국의 옛 주거 문화를 느낄 수 있습니다."
    },
    {
        "name": "인사동",
        "lat": 37.5740,
        "lon": 126.9855,
        "category": "전통·문화",
        "desc": "전통 공예품과 갤러리, 전통 찻집 등을 경험할 수 있는 문화 거리입니다."
    },
    {
        "name": "홍대거리",
        "lat": 37.5563,
        "lon": 126.9236,
        "category": "문화·쇼핑",
        "desc": "개성 있는 상점과 거리 공연, 음악과 패션 문화를 즐길 수 있는 활기찬 거리입니다."
    },
    {
        "name": "동대문디자인플라자(DDP)",
        "lat": 37.5669,
        "lon": 127.0095,
        "category": "건축·전시",
        "desc": "독특한 곡선형 건축물로 유명하며 다양한 전시와 디자인 행사를 관람할 수 있습니다."
    },
    {
        "name": "광장시장",
        "lat": 37.5700,
        "lon": 126.9997,
        "category": "시장·먹거리",
        "desc": "빈대떡과 김밥 등 다양한 한국 전통 음식을 맛볼 수 있는 전통시장입니다."
    },
    {
        "name": "롯데월드",
        "lat": 37.5111,
        "lon": 127.0982,
        "category": "테마파크",
        "desc": "다양한 놀이기구와 퍼레이드, 아이스링크 등을 즐길 수 있는 대형 테마파크입니다."
    },
    {
        "name": "청와대",
        "lat": 37.5866,
        "lon": 126.9748,
        "category": "역사·건축",
        "desc": "대한민국 대통령의 옛 집무 공간으로 역사적인 의미와 아름다운 건축물을 볼 수 있습니다."
    }
]

# 서울 지도 만들기
seoul_map = folium.Map(
    location=[37.5665, 126.9780],
    zoom_start=12,
    tiles="OpenStreetMap"
)

# 지도에 관광지 마커 표시
for i, spot in enumerate(spots, start=1):

    popup_text = f"""
    <b>{i}. {spot['name']}</b><br>
    <b>분류:</b> {spot['category']}<br>
    {spot['desc']}
    """

    folium.Marker(
        location=[spot["lat"], spot["lon"]],
        tooltip=f"{i}. {spot['name']}",
        popup=folium.Popup(popup_text, max_width=300),
        icon=folium.DivIcon(
            html=f"""
            <div style="
                background-color:#1769aa;
                color:white;
                border:2px solid white;
                border-radius:50%;
                width:30px;
                height:30px;
                text-align:center;
                line-height:26px;
                font-weight:bold;
                box-shadow:0 1px 4px #555;">
                {i}
            </div>
            """
        )
    ).add_to(seoul_map)

# 지도 출력
st.subheader("📍 서울 주요 관광지 지도")

st_folium(
    seoul_map,
    width=None,
    height=560,
    use_container_width=True
)

# 관광지 설명
st.subheader("✨ 관광지 TOP 10 소개")

# 두 개의 열로 표시
col1, col2 = st.columns(2)

for index, spot in enumerate(spots):

    if index % 2 == 0:
        with col1:
            st.markdown(f"### {index + 1}. {spot['name']}")
            st.caption(spot["category"])
            st.write(spot["desc"])
            st.divider()

    else:
        with col2:
            st.markdown(f"### {index + 1}. {spot['name']}")
            st.caption(spot["category"])
            st.write(spot["desc"])
            st.divider()

# 하단 안내
st.info(
    "※ 외국인 관광객에게 잘 알려진 서울의 대표 관광지를 "
    "소개한 목록이며 공식 선호도 순위는 아닙니다."
)

st.caption("🗺️ 지도는 OpenStreetMap을 사용하며 인터넷 연결이 필요합니다.")
