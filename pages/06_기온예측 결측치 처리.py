
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# ==========================================
# 1. 페이지 설정
# ==========================================

st.set_page_config(
    page_title="미래 기온 예측 분석",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 월별 미래 기온 예측 분석")
st.write(
    "과거 기온 데이터를 이용하여 세 가지 알고리즘으로 "
    "미래 평균기온을 예측합니다."
)


# ==========================================
# 2. 데이터 불러오기
# ==========================================

@st.cache_data
def load_data():

    # pages 폴더의 상위 폴더에 있는 CSV 파일
    file_path = (
        Path(__file__).resolve().parent.parent
        / "temperature.csv"
    )

    if not file_path.exists():
        raise FileNotFoundError(
            "상위 폴더에서 temperature.csv를 찾을 수 없습니다."
        )

    # 한글 인코딩 자동 처리
    df = None

    for encoding in [
        "cp949",
        "euc-kr",
        "utf-8-sig",
        "utf-8"
    ]:
        try:
            df = pd.read_csv(
                file_path,
                encoding=encoding
            )
            break

        except UnicodeDecodeError:
            continue

    if df is None:
        raise ValueError(
            "CSV 파일의 인코딩을 확인해주세요."
        )

    df.columns = df.columns.astype(str).str.strip()

    # 필요한 컬럼
    required = [
        "일시",
        "평균기온(℃)"
    ]

    for col in required:
        if col not in df.columns:
            raise ValueError(
                f"'{col}' 컬럼이 없습니다."
            )

    # 날짜 변환
    df["날짜"] = pd.to_datetime(
        df["일시"].astype(str).str.strip(),
        format="%b-%y",
        errors="coerce"
    )

    # 연도와 월 추출
    df["연도"] = df["날짜"].dt.year
    df["월"] = df["날짜"].dt.month

    # 평균기온 숫자 변환
    df["평균기온(℃)"] = pd.to_numeric(
        df["평균기온(℃)"],
        errors="coerce"
    )

    # 결측값 제거
    df = df.dropna(
        subset=["연도", "월", "평균기온(℃)"]
    )

    df["연도"] = df["연도"].astype(int)
    df["월"] = df["월"].astype(int)

    # 연도와 월별 평균기온 계산
    monthly = (
        df.groupby(
            ["연도", "월"],
            as_index=False
        )["평균기온(℃)"]
        .mean()
        .sort_values("연도")
    )

    return monthly


try:
    data = load_data()

except Exception as e:
    st.error(f"데이터 오류: {e}")
    st.stop()


# ==========================================
# 3. 분석 기간 설정
# ==========================================

START_YEAR = 1907
END_YEAR = 2025

# 실제 데이터에서 1907~2025년 자료만 사용
historical_data = data[
    (data["연도"] >= START_YEAR)
    & (data["연도"] <= END_YEAR)
].copy()

if historical_data.empty:
    st.error("분석할 과거 데이터가 없습니다.")
    st.stop()


actual_start = historical_data["연도"].min()
actual_end = historical_data["연도"].max()

st.info(
    f"분석 요청 기간: {START_YEAR}~{END_YEAR}년 | "
    f"실제 CSV 데이터 기간: {actual_start}~{actual_end}년"
)


# ==========================================
# 4. 월과 예측 연도 선택
# ==========================================

st.subheader("📅 분석 조건 선택")

col1, col2 = st.columns(2)

with col1:
    selected_month = st.selectbox(
        "분석할 월을 선택하세요.",
        options=list(range(1, 13)),
        format_func=lambda x: f"{x}월",
        index=6
    )

with col2:
    selected_year = st.number_input(
        "예측하고 싶은 연도를 입력하세요.",
        min_value=actual_end + 1,
        max_value=2100,
        value=min(actual_end + 10, 2100),
        step=1
    )

selected_year = int(selected_year)


# ==========================================
# 5. 선택한 월의 데이터 추출
# ==========================================

month_data = historical_data[
    historical_data["월"] == selected_month
].copy()

month_data = (
    month_data
    .sort_values("연도")
    .dropna(subset=["평균기온(℃)"])
)

if len(month_data) < 3:
    st.error(
        "예측을 위해서는 최소 3개 이상의 연도 데이터가 필요합니다."
    )
    st.stop()

years = month_data["연도"].to_numpy(dtype=float)
temps = month_data["평균기온(℃)"].to_numpy(dtype=float)

# 수치 계산을 안정적으로 하기 위해 연도를 중심화
base_year = years.mean()
x = years - base_year

future_years = np.arange(
    int(years.max()) + 1,
    selected_year + 1
)

future_x = future_years - base_year


# ==========================================
# 6. 알고리즘 1: 선형회귀
# ==========================================

# 과거 데이터의 전체적인 직선 추세 계산
linear_coef = np.polyfit(
    x,
    temps,
    1
)

linear_historical = np.polyval(
    linear_coef,
    x
)

linear_future = np.polyval(
    linear_coef,
    future_x
)


# ==========================================
# 7. 알고리즘 2: 2차 다항회귀
# ==========================================

# 기온 변화의 곡선 형태 분석
poly_coef = np.polyfit(
    x,
    temps,
    2
)

poly_historical = np.polyval(
    poly_coef,
    x
)

poly_future = np.polyval(
    poly_coef,
    future_x
)


# ==========================================
# 8. 알고리즘 3: 이동평균
# ==========================================

# 최근 10개의 관측값을 이용한 이동평균
temp_series = pd.Series(temps)

moving_average = (
    temp_series
    .rolling(window=10, min_periods=1)
    .mean()
    .to_numpy()
)

# 마지막 10개 관측값의 평균
last_10_average = temp_series.tail(10).mean()

# 미래는 최근 10개 관측값의 평균으로 예측
moving_future = np.full(
    len(future_years),
    last_10_average
)


# ==========================================
# 9. 예측 결과 계산
# ==========================================

linear_prediction = float(linear_future[-1])
poly_prediction = float(poly_future[-1])
moving_prediction = float(moving_future[-1])


# ==========================================
# 10. 예측 결과 표시
# ==========================================

st.divider()

st.subheader(
    f"🔮 {selected_month}월 {selected_year}년 평균기온 예측"
)

c1, c2, c3 = st.columns(3)

with c1:
    st.metric(
        "① 선형회귀",
        f"{linear_prediction:.2f} ℃"
    )

with c2:
    st.metric(
        "② 2차 다항회귀",
        f"{poly_prediction:.2f} ℃"
    )

with c3:
    st.metric(
        "③ 이동평균",
        f"{moving_prediction:.2f} ℃"
    )


# ==========================================
# 11. 그래프 생성
# ==========================================

st.divider()

st.subheader("📈 실제 기온과 알고리즘별 예측 비교")

fig = go.Figure()

# 실제 평균기온
fig.add_trace(
    go.Scatter(
        x=years,
        y=temps,
        mode="lines+markers",
        name="실제 평균기온",
        line=dict(
            color="#333333",
            width=3
        ),
        marker=dict(size=5)
    )
)

# 선형회귀
fig.add_trace(
    go.Scatter(
        x=np.concatenate([years, future_years]),
        y=np.concatenate([
            linear_historical,
            linear_future
        ]),
        mode="lines",
        name="① 선형회귀",
        line=dict(
            color="#FF69B4",
            width=3,
            dash="dash"
        )
    )
)

# 2차 다항회귀
fig.add_trace(
    go.Scatter(
        x=np.concatenate([years, future_years]),
        y=np.concatenate([
            poly_historical,
            poly_future
        ]),
        mode="lines",
        name="② 2차 다항회귀",
        line=dict(
            color="#4169E1",
            width=3,
            dash="dot"
        )
    )
)

# 이동평균
fig.add_trace(
    go.Scatter(
        x=np.concatenate([years, future_years]),
        y=np.concatenate([
            moving_average,
            moving_future
        ]),
        mode="lines",
        name="③ 이동평균",
        line=dict(
            color="#00A878",
            width=3,
            dash="dashdot"
        )
    )
)

# 예측 목표 연도 표시
fig.add_vline(
    x=selected_year,
    line_dash="dot",
    line_color="gray",
    annotation_text=f"{selected_year}년 예측",
    annotation_position="top"
)

# 그래프 디자인
fig.update_layout(
    title=dict(
        text=f"{selected_month}월 평균기온 및 미래 예측",
        x=0.5,
        xanchor="center",
        font=dict(size=23)
    ),

    xaxis_title="연도",
    yaxis_title="평균기온 (℃)",

    template="plotly_white",
    height=650,

    hovermode="x unified",

    legend=dict(
        title="그래프 범례",
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5
    ),

    margin=dict(
        l=50,
        r=40,
        t=110,
        b=60
    )
)

fig.update_xaxes(
    showgrid=True,
    dtick=10
)

fig.update_yaxes(
    showgrid=True,
    zeroline=True
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ==========================================
# 12. 알고리즘별 작동 방식 설명
# ==========================================

st.divider()

st.subheader("🧠 알고리즘별 작동 원리")

with st.expander("① 선형회귀 - 직선으로 미래 예측", expanded=True):

    st.markdown(
        """
        **작동 원리**

        - 과거의 연도별 평균기온을 모두 확인합니다.
        - 전체 기온의 상승 또는 하락 추세를 직선으로 계산합니다.
        - 그 직선을 미래 연도까지 연장하여 예측합니다.

        **그래프 읽는 방법**

        핫핑크 점선이 일정한 방향으로 곧게 이어집니다.

        - 오른쪽으로 올라가면 기온 상승 추세
        - 오른쪽으로 내려가면 기온 하락 추세
        - 기울기가 완만하면 변화가 적은 추세

        **예측 결과**

        선형회귀 예측:
        """
    )

    st.metric(
        "예측 평균기온",
        f"{linear_prediction:.2f} ℃"
    )


with st.expander("② 2차 다항회귀 - 곡선으로 미래 예측"):

    st.markdown(
        """
        **작동 원리**

        - 과거 기온의 변화가 직선이 아닐 수 있다는 점을 반영합니다.
        - 2차 방정식을 사용하여 곡선 형태를 계산합니다.
        - 기온이 상승하거나 하락하는 변화의 굴곡을 표현합니다.

        **그래프 읽는 방법**

        파란색 점선이 휘어지는 모습을 확인하세요.

        - 위로 휘어지면 상승 변화가 커지는 형태
        - 아래로 휘어지면 상승세가 약해지거나 하락하는 형태
        - 곡선의 방향이 달라지면 추세 변화가 반영된 것입니다.

        단, 먼 미래에서는 곡선이 실제 기후와 크게 달라질 수 있습니다.

        **예측 결과**
        """
    )

    st.metric(
        "예측 평균기온",
        f"{poly_prediction:.2f} ℃"
    )


with st.expander("③ 이동평균 - 최근 기온의 평균으로 예측"):

    st.markdown(
        """
        **작동 원리**

        - 가장 최근의 10개 관측값을 선택합니다.
        - 10개 기온의 평균을 계산합니다.
        - 이 평균을 미래 기온의 예측값으로 사용합니다.

        **그래프 읽는 방법**

        초록색 선은 최근 기온의 평균을 나타냅니다.

        - 과거 구간에서는 최근 10개 관측값의 평균이 움직입니다.
        - 미래 구간에서는 최근 10개 관측값의 평균을 유지합니다.
        - 따라서 미래 예측선이 수평으로 이어집니다.

        **예측 결과**
        """
    )

    st.metric(
        "예측 평균기온",
        f"{moving_prediction:.2f} ℃"
    )


# ==========================================
# 13. 데이터 확인
# ==========================================

st.divider()

with st.expander("📋 실제 분석 데이터 확인"):

    display_df = month_data[
        ["연도", "월", "평균기온(℃)"]
    ].copy()

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


# ==========================================
# 14. 알고리즘 결과 비교
# ==========================================

st.subheader("📊 세 가지 알고리즘 예측 결과 비교")

result_df = pd.DataFrame({
    "알고리즘": [
        "선형회귀",
        "2차 다항회귀",
        "이동평균"
    ],
    "예측 연도": [
        selected_year,
        selected_year,
        selected_year
    ],
    "예측 평균기온(℃)": [
        round(linear_prediction, 2),
        round(poly_prediction, 2),
        round(moving_prediction, 2)
    ]
})

st.dataframe(
    result_df,
    use_container_width=True,
    hide_index=True
)

st.caption(
    "※ 예측값은 선택한 월의 과거 평균기온을 이용한 통계적 추정치이며, "
    "실제 미래 기온을 보장하지 않습니다."
)
