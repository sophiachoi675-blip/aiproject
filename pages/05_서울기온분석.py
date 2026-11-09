
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# --------------------------------
# 1. 페이지 설정
# --------------------------------

st.set_page_config(
    page_title="월별 기온 분석",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 월별 기온 분석")
st.write("월을 선택하여 전체 연도의 최고기온과 최저기온을 비교해 보세요.")


# --------------------------------
# 2. CSV 파일 불러오기
# --------------------------------

@st.cache_data
def load_data():

    # pages 폴더의 상위 폴더에서 CSV 파일 찾기
    file_path = (
        Path(__file__).resolve().parent.parent
        / "temperature.csv"
    )

    if not file_path.exists():
        raise FileNotFoundError(
            "상위 폴더에서 temperature.csv 파일을 찾을 수 없습니다."
        )

    # 한글 인코딩 처리
    encodings = ["cp949", "euc-kr", "utf-8-sig", "utf-8"]

    df = None

    for encoding in encodings:
        try:
            df = pd.read_csv(
                file_path,
                encoding=encoding
            )
            break

        except UnicodeDecodeError:
            continue

    if df is None:
        raise ValueError("CSV 파일의 인코딩을 확인해주세요.")

    # 컬럼명 공백 제거
    df.columns = df.columns.astype(str).str.strip()

    # 필요한 컬럼 확인
    required_columns = [
        "일시",
        "최고기온(℃)",
        "최저기온(℃)"
    ]

    for col in required_columns:
        if col not in df.columns:
            raise ValueError(
                f"CSV 파일에 {col} 컬럼이 없습니다."
            )

    # 기온 데이터를 숫자로 변환
    for col in ["최고기온(℃)", "최저기온(℃)"]:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    # 영문 월 이름을 숫자로 변환
    month_dict = {
        "Jan": 1,
        "Feb": 2,
        "Mar": 3,
        "Apr": 4,
        "May": 5,
        "Jun": 6,
        "Jul": 7,
        "Aug": 8,
        "Sep": 9,
        "Oct": 10,
        "Nov": 11,
        "Dec": 12
    }

    # 연도와 월 추출
    date_parts = (
        df["일시"]
        .astype(str)
        .str.strip()
        .str.split("-", expand=True)
    )

    df["월"] = date_parts[0].str.title().map(month_dict)

    # 현재 데이터의 두 자리 연도는 2007~2026년
    df["연도"] = pd.to_numeric(
        date_parts[1],
        errors="coerce"
    ) + 2000

    # 잘못된 날짜 및 결측 연도 제거
    df = df.dropna(
        subset=["연도", "월"]
    )

    df["연도"] = df["연도"].astype(int)
    df["월"] = df["월"].astype(int)

    # 같은 연도와 월에 데이터가 여러 개라면 평균 계산
    df = (
        df.groupby(
            ["연도", "월"],
            as_index=False
        )[
            ["최고기온(℃)", "최저기온(℃)"]
        ]
        .mean()
        .sort_values("연도")
    )

    return df


# --------------------------------
# 3. 데이터 실행
# --------------------------------

try:
    df = load_data()

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()


# --------------------------------
# 4. 월 선택
# --------------------------------

st.subheader("📅 분석할 월 선택")

selected_month = st.selectbox(
    "월을 선택하세요.",
    options=list(range(1, 13)),
    format_func=lambda x: f"{x}월"
)


# --------------------------------
# 5. 선택한 월 데이터 추출
# --------------------------------

month_df = df[
    df["월"] == selected_month
].copy()

month_df = month_df.sort_values("연도")


# --------------------------------
# 6. 그래프 생성
# --------------------------------

if month_df.empty:

    st.warning("선택한 월의 데이터가 없습니다.")

else:

    fig = go.Figure()

    # 최고기온 - 핫핑크
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
                size=8
            )
        )
    )

    # 최저기온 - 하늘색
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
                size=8
            )
        )
    )

    # 그래프 제목 및 설정
    fig.update_layout(

        title=dict(
            text="월별 기온 분석",
            x=0.5,
            xanchor="center",
            font=dict(size=25)
        ),

        xaxis_title="연도",
        yaxis_title="온도(℃)",

        legend=dict(
            title="범례",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),

        hovermode="x unified",

        template="plotly_white",

        height=600,

        font=dict(size=14)
    )

    fig.update_xaxes(
        title_font=dict(size=16),
        tickmode="linear",
        dtick=2
    )

    fig.update_yaxes(
        title_font=dict(size=16),
        showgrid=True,
        zeroline=True
    )

    # Streamlit 그래프 출력
    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # --------------------------------
    # 7. 분석 데이터 표시
    # --------------------------------

    st.subheader("📊 선택한 월의 기온 데이터")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "최고기온",
            f"{month_df['최고기온(℃)'].max():.1f}℃"
        )

    with col2:
        st.metric(
            "최저기온",
            f"{month_df['최저기온(℃)'].min():.1f}℃"
        )

    # 데이터 표
    with st.expander("상세 데이터 확인하기"):

        st.dataframe(
            month_df[
                ["연도", "최고기온(℃)", "최저기온(℃)"]
            ],
            use_container_width=True,
            hide_index=True
        )


