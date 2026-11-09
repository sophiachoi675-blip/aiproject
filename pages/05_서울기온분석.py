
from pathlib import Path
import datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# 페이지 설정
st.set_page_config(
    page_title="월별 기온 분석",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 월별 기온 분석")
st.write("원하는 월을 선택하면 전체 연도의 최고기온과 최저기온을 비교할 수 있습니다.")


# CSV 데이터 불러오기
@st.cache_data
def load_data():

    file_path = Path(__file__).resolve().parent / "temperature.csv"

    if not file_path.exists():
        st.error("temperature.csv 파일을 찾을 수 없습니다.")
        st.stop()

    # 한글 인코딩 처리
    encodings = ["cp949", "euc-kr", "utf-8-sig", "utf-8"]
    df = None

    for encoding in encodings:
        try:
            df = pd.read_csv(file_path, encoding=encoding)
            break
        except UnicodeDecodeError:
            continue

    if df is None:
        raise ValueError("CSV 파일 인코딩을 확인해주세요.")

    df.columns = df.columns.astype(str).str.strip()

    # 필요한 컬럼 확인
    required_columns = [
        "일시",
        "최고기온(℃)",
        "최저기온(℃)"
    ]

    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"{col} 컬럼이 없습니다.")

    # 기온을 숫자로 변환
    for col in ["최고기온(℃)", "최저기온(℃)"]:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    # 연도와 월 추출
    # 두 자리 연도의 세기 변화를 행 순서로 복원
    month_numbers = []
    full_years = []

    century = 1900
    previous_short_year = None

    for value in df["일시"].astype(str).str.strip():

        try:
            month_text, short_year_text = value.split("-")

            month_number = datetime.datetime.strptime(
                month_text.title(), "%b"
            ).month

            short_year = int(short_year_text)

            if (
                previous_short_year is not None
                and short_year < previous_short_year
            ):
                century += 100

            full_year = century + short_year

            month_numbers.append(month_number)
            full_years.append(full_year)

            previous_short_year = short_year

        except (ValueError, TypeError):
            month_numbers.append(None)
            full_years.append(None)

    df["월"] = month_numbers
    df["연도"] = full_years

    df = df.dropna(subset=["연도", "월"])

    df["연도"] = df["연도"].astype(int)
    df["월"] = df["월"].astype(int)

    # 연도와 월별 데이터 정리
    df = (
        df.groupby(["연도", "월"], as_index=False)[
            ["최고기온(℃)", "최저기온(℃)"]
        ]
        .mean()
        .sort_values("연도")
    )

    return df


# 데이터 불러오기
try:
    df = load_data()

except Exception as error:
    st.error(f"데이터 오류: {error}")
    st.stop()


# 월 선택
selected_month = st.selectbox(
    "분석할 월을 선택하세요.",
    options=list(range(1, 13)),
    format_func=lambda month: f"{month}월"
)


# 선택한 월의 데이터 추출
month_df = df[
    df["월"] == selected_month
].copy()

month_df = month_df.sort_values("연도")


# 그래프 생성
if month_df.empty:

    st.warning("선택한 월의 데이터가 없습니다.")

else:

    fig = go.Figure()

    # 최고기온 그래프 - 핫핑크
    fig.add_trace(
        go.Scatter(
            x=month_df["연도"],
            y=month_df["최고기온(℃)"],
            mode="lines+markers",
            name="최고기온",
            line=dict(
                color="#FF69B4",
                width=3
            ),
            marker=dict(
                color="#FF69B4",
                size=7
            ),
            connectgaps=False
        )
    )

    # 최저기온 그래프 - 하늘색
    fig.add_trace(
        go.Scatter(
            x=month_df["연도"],
            y=month_df["최저기온(℃)"],
            mode="lines+markers",
            name="최저기온",
            line=dict(
                color="#87CEEB",
                width=3
            ),
            marker=dict(
                color="#87CEEB",
                size=7
            ),
            connectgaps=False
        )
    )

    # 그래프 제목과 축 설정
    fig.update_layout(
        title={
            "text": "월별 기온 분석",
            "x": 0.5,
            "xanchor": "center"
        },

        xaxis_title="연도",
        yaxis_title="온도(℃)",

        legend_title="범례",
        hovermode="x unified",

        template="plotly_white",
        height=600,

        margin=dict(
            l=40,
            r=40,
            t=80,
            b=50
        )
    )

    fig.update_xaxes(dtick=5)

    # 그래프 출력
    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.caption(
        f"선택한 월: {selected_month}월 | "
        f"데이터 연도: {month_df['연도'].min()}년 ~ "
        f"{month_df['연도'].max()}년"
    )

    # 데이터 표 확인
    with st.expander("그래프에 사용된 데이터 보기"):

        display_df = month_df[
            ["연도", "최고기온(℃)", "최저기온(℃)"]
        ]

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
