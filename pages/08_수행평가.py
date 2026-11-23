
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# 페이지 설정
st.set_page_config(
    page_title="지역별 범죄 통계 분석",
    page_icon="📊",
    layout="wide"
)

# CSV 파일 경로 (pages 폴더의 상위 폴더)
BASE_DIR = Path(__file__).resolve().parent.parent

CSV_FILE = BASE_DIR / "경찰청_범죄 발생 지역별 통계_20251231.csv"


# 데이터 불러오기
@st.cache_data
def load_data():
    df = pd.read_csv(CSV_FILE, encoding="cp949")

    # 숫자 데이터 변환
    for col in df.columns[2:]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df


# 데이터 오류 확인
try:
    df = load_data()
except FileNotFoundError:
    st.error("CSV 파일을 찾을 수 없습니다.")
    st.info("CSV 파일이 파이썬 파일의 상위 폴더에 있는지 확인해 주세요.")
    st.stop()
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()


# 제목
st.title("🚨 지역별 범죄 발생 통계 분석")
st.markdown(
    "경찰청 데이터를 활용하여 지역별 범죄 종류와 발생 비율을 분석합니다."
)

st.divider()


# 지역 선택
region_columns = df.columns[2:].tolist()

selected_region = st.selectbox(
    "📍 분석할 지역을 선택하세요.",
    region_columns
)


# 선택 지역의 범죄 데이터 추출
crime_data = df[["범죄대분류", "범죄중분류", selected_region]].copy()

crime_data = crime_data.rename(
    columns={selected_region: "발생건수"}
)

# 범죄 종류별 합계 계산
crime_data = crime_data.groupby(
    ["범죄대분류", "범죄중분류"],
    as_index=False
)["발생건수"].sum()

# 발생 건수가 0보다 큰 항목만 사용
crime_data = crime_data[
    crime_data["발생건수"] > 0
].copy()

# 발생 건수 기준 내림차순 정렬
crime_data = crime_data.sort_values(
    by="발생건수",
    ascending=False
)

# 전체 범죄 발생 건수
total_crimes = crime_data["발생건수"].sum()

if total_crimes == 0:
    st.warning("선택한 지역의 범죄 발생 데이터가 없습니다.")
    st.stop()

# 비율 계산
crime_data["비율"] = (
    crime_data["발생건수"] / total_crimes * 100
)

crime_data["순위"] = range(1, len(crime_data) + 1)


# 주요 통계
st.subheader(f"📌 {selected_region} 범죄 통계")

col1, col2, col3 = st.columns(3)

col1.metric(
    "총 범죄 발생 건수",
    f"{total_crimes:,.0f}건"
)

col2.metric(
    "범죄 종류 수",
    f"{len(crime_data)}종"
)

col3.metric(
    "발생 비율 1위",
    crime_data.iloc[0]["범죄중분류"]
)

st.divider()


# 그래프 색상 설정
# 1위는 빨간색, 나머지는 파란색 그라데이션
blue_gradient = [
    "#2563EB",
    "#3B82F6",
    "#60A5FA",
    "#93C5FD",
    "#BFDBFE",
    "#DBEAFE"
]

colors = ["#EF4444"]

for i in range(1, len(crime_data)):
    colors.append(
        blue_gradient[
            min(i - 1, len(blue_gradient) - 1)
        ]
    )

# 그래프 생성
st.subheader("📊 범죄 종류별 발생 비율")

fig = px.bar(
    crime_data,
    x="범죄중분류",
    y="비율",
    color="범죄중분류",
    color_discrete_sequence=colors,
    custom_data=["발생건수", "범죄대분류", "순위"],
    labels={
        "범죄중분류": "범죄 종류",
        "비율": "발생 비율 (%)"
    },
    title=f"{selected_region} 범죄 종류별 발생 비율"
)

fig.update_traces(
    hovertemplate=
    "<b>%{x}</b><br>" +
    "범죄 대분류: %{customdata[1]}<br>" +
    "발생 건수: %{customdata[0]:,.0f}건<br>" +
    "발생 비율: %{y:.2f}%<br>" +
    "순위: %{customdata[2]}위" +
    "<extra></extra>"
)

fig.update_layout(
    template="plotly_white",
    showlegend=False,
    xaxis_title="범죄 종류",
    yaxis_title="발생 비율 (%)",
    height=600,
    hovermode="x unified",
    font=dict(
        family="Malgun Gothic, Arial",
        size=12
    ),
    margin=dict(
        l=40,
        r=30,
        t=70,
        b=100
    )
)

fig.update_xaxes(
    tickangle=-45
)

fig.update_yaxes(
    ticksuffix="%"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# 데이터 표
st.divider()

st.subheader("📋 범죄 종류별 상세 데이터")

display_data = crime_data[
    ["순위", "범죄대분류", "범죄중분류", "발생건수", "비율"]
].copy()

display_data["발생건수"] = display_data["발생건수"].map(
    lambda x: f"{x:,.0f}건"
)

display_data["비율"] = display_data["비율"].map(
    lambda x: f"{x:.2f}%"
)

st.dataframe(
    display_data,
    use_container_width=True,
    hide_index=True
)

st.caption(
    "자료 출처: 경찰청 범죄 발생 지역별 통계 | "
    "비율은 선택 지역의 전체 범죄 발생 건수를 기준으로 계산했습니다."
)

