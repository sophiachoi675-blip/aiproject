
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import math
import re
from pathlib import Path

# ==========================================
# 1. 기본 화면 설정
# ==========================================

st.set_page_config(
    page_title="용산구 연령별 인구 분석",
    page_icon="📊",
    layout="wide"
)

st.title("📊 용산구 연령별 인구 분석")
st.caption("행정구역, 성별, 연도를 선택하여 연령별 인구수를 확인하세요.")

# ==========================================
# 2. CSV 파일 경로 설정
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "POPULATION (2).csv"

# ==========================================
# 3. CSV 파일 불러오기
# 한글 인코딩 깨짐 방지
# ==========================================

@st.cache_data
def load_data():

    encodings = [
        "cp949",
        "euc-kr",
        "utf-8-sig",
        "utf-8"
    ]

    last_error = None

    for encoding in encodings:
        try:
            data = pd.read_csv(
                CSV_PATH,
                encoding=encoding
            )
            return data

        except UnicodeDecodeError as error:
            last_error = error

    raise ValueError(
        "CSV 파일의 한글 인코딩을 확인해 주세요."
    ) from last_error


try:
    df = load_data()

except FileNotFoundError:
    st.error(
        f"CSV 파일을 찾을 수 없습니다.\n\n"
        f"파일 위치: {CSV_PATH}"
    )
    st.stop()

except Exception as error:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {error}")
    st.stop()


# ==========================================
# 4. 데이터 정리
# ==========================================

if "행정구역" not in df.columns:
    st.error("행정구역 열을 찾을 수 없습니다.")
    st.stop()

# 숫자 데이터 변환
for column in df.columns:

    if column != "행정구역":

        df[column] = pd.to_numeric(
            df[column].astype(str).str.replace(
                ",", "", regex=False
            ),
            errors="coerce"
        )


# 행정구역 코드 제거
def clean_region_name(name):

    return re.sub(
        r"\s*\(\d+\)\s*$",
        "",
        str(name)
    ).strip()


df["표시행정구역"] = df["행정구역"].apply(
    clean_region_name
)


# ==========================================
# 5. 연도 및 연령대 설정
# ==========================================

years = [
    2020, 2021, 2022,
    2023, 2024, 2025
]

age_groups = [
    "0~9세",
    "10~19세",
    "20~29세",
    "30~39세",
    "40~49세",
    "50~59세",
    "60~69세",
    "70~79세",
    "80~89세",
    "90~99세",
    "100세 이상"
]


# ==========================================
# 6. 분석 조건 선택
# ==========================================

st.subheader("🔎 분석 조건 선택")

col1, col2, col3 = st.columns(3)

with col1:

    region_options = (
        df["표시행정구역"]
        .dropna()
        .drop_duplicates()
        .tolist()
    )

    selected_region = st.selectbox(
        "행정구역 선택",
        region_options
    )


with col2:

    gender_options = {
        "전체": "",
        "남성": "남",
        "여성": "여"
    }

    selected_gender = st.selectbox(
        "성별 선택",
        list(gender_options.keys())
    )


with col3:

    selected_year = st.selectbox(
        "연도 선택",
        years,
        index=len(years) - 1
    )


# ==========================================
# 7. 선택한 행정구역 데이터 찾기
# ==========================================

selected_rows = df[
    df["표시행정구역"] == selected_region
]

if selected_rows.empty:

    st.error("선택한 행정구역 데이터가 없습니다.")
    st.stop()

region_data = selected_rows.iloc[0]


# ==========================================
# 8. 연령별 인구수 추출
# ==========================================

gender_code = gender_options[selected_gender]

population_values = []
missing_columns = []

for age in age_groups:

    if gender_code == "":

        column_name = (
            f"{selected_year}년_거주자_{age}"
        )

    else:

        column_name = (
            f"{selected_year}년_{gender_code}_거주자_{age}"
        )

    if column_name in df.columns:

        value = region_data[column_name]

        population_values.append(
            0 if pd.isna(value) else int(value)
        )

    else:

        missing_columns.append(column_name)
        population_values.append(0)


if missing_columns:

    st.warning(
        "일부 연령대 데이터 열을 찾지 못했습니다. "
        "CSV 파일의 열 이름을 확인해 주세요."
    )


chart_data = pd.DataFrame({
    "연령대": age_groups,
    "인구수": population_values
})

total_population = sum(population_values)


# ==========================================
# 9. 주요 정보 표시
# ==========================================

metric1, metric2, metric3 = st.columns(3)

metric1.metric(
    "선택 행정구역",
    selected_region
)

metric2.metric(
    "선택 연도",
    f"{selected_year}년"
)

metric3.metric(
    "연령별 인구 합계",
    f"{total_population:,}명"
)


# ==========================================
# 10. 핫핑크 꺾은선 그래프
# ==========================================

st.subheader("📈 연령대별 인구수")

fig = go.Figure()

fig.add_trace(
    go.Scatter(

        x=chart_data["연령대"],
        y=chart_data["인구수"],

        mode="lines+markers",

        name="인구수",

        line=dict(
            color="#FF1493",
            width=4
        ),

        marker=dict(
            color="#FF1493",
            size=9,
            line=dict(
                color="#FFFFFF",
                width=1
            )
        ),

        hovertemplate=(
            "연령대: %{x}<br>"
            "인구수: %{y:,.0f}명"
            "<extra></extra>"
        )
    )
)


# ==========================================
# 11. 그래프 디자인 및 축 설정
# ==========================================

max_population = max(population_values)

y_axis_max = max(
    1000,
    math.ceil(max_population / 1000) * 1000
)

fig.update_layout(

    title=(
        f"{selected_region} | "
        f"{selected_year}년 | "
        f"{selected_gender} 연령별 인구"
    ),

    xaxis_title="나이",
    yaxis_title="인구수 (명)",

    height=570,

    template="plotly_white",

    font=dict(
        family="sans-serif",
        size=13,
        color="#333333"
    ),

    hovermode="x unified",

    margin=dict(
        l=35,
        r=25,
        t=75,
        b=65
    ),

    showlegend=False
)


# 가로축: 10살 단위 구분

fig.update_xaxes(

    type="category",

    categoryorder="array",

    categoryarray=age_groups,

    tickmode="array",

    tickvals=age_groups,

    ticktext=age_groups,

    showgrid=True,

    gridcolor="#E8E8E8",

    gridwidth=1
)


# 세로축: 1,000명 단위 구분

fig.update_yaxes(

    rangemode="tozero",

    range=[0, y_axis_max],

    dtick=1000,

    tickformat=",",

    ticksuffix="명",

    showgrid=True,

    gridcolor="#E8E8E8",

    gridwidth=1,

    zeroline=True,

    zerolinecolor="#BBBBBB"
)


# 그래프 출력

st.plotly_chart(
    fig,
    use_container_width=True
)


# ==========================================
# 12. 연령별 인구수 표
# ==========================================

with st.expander("📋 연령대별 인구수 자세히 보기"):

    display_data = chart_data.copy()

    display_data["인구수"] = (
        display_data["인구수"]
        .map(lambda x: f"{x:,}명")
    )

    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True
    )


# ==========================================
# 13. 하단 안내
# ==========================================

st.caption(
    "자료: POPULATION (2).csv | "
    "연령대는 10살 단위이며, "
    "100세 이상은 별도 구간입니다."
)
