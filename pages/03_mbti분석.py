
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 페이지 설정
st.set_page_config(
    page_title="국가별 MBTI 비율 분석",
    page_icon="🌍",
    layout="wide"
)

# 데이터 불러오기
@st.cache_data
def load_data():
    df = pd.read_csv("countriesMBTI_16types.csv")

    df["Country"] = df["Country"].astype(str).str.strip()

    mbti_columns = [
        col for col in df.columns if col != "Country"
    ]

    for col in mbti_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["Country"])

    return df, mbti_columns


try:
    data, mbti_columns = load_data()

except FileNotFoundError:
    st.error(
        "CSV 파일을 찾을 수 없습니다. "
        "app.py와 같은 폴더에 넣어주세요."
    )
    st.stop()


# 제목
st.title("🌍 국가별 MBTI 비율 분석")

st.write(
    "국가를 선택하면 해당 국가의 "
    "MBTI 16가지 유형별 비율을 확인할 수 있습니다."
)

st.divider()


# 국가 선택
country_list = sorted(data["Country"].unique().tolist())

selected_country = st.selectbox(
    "📍 분석할 국가를 선택하세요.",
    country_list,
    index=(
        country_list.index("South Korea")
        if "South Korea" in country_list
        else 0
    )
)


# 선택한 국가 데이터
country_data = data[
    data["Country"] == selected_country
].iloc[0]


# MBTI 비율 정리
chart_data = pd.DataFrame({
    "MBTI": mbti_columns,
    "비율": [
        float(country_data[mbti])
        for mbti in mbti_columns
    ]
})

# 비율 높은 순서로 정렬
chart_data = chart_data.sort_values(
    "비율",
    ascending=False
).reset_index(drop=True)

# 백분율 변환
chart_data["백분율"] = chart_data["비율"] * 100


# 그래프 색상
# 1위는 빨간색
# 나머지는 파란색 그라데이션

blue_gradient = [
    "#1565C0",
    "#1976D2",
    "#1E88E5",
    "#42A5F5",
    "#64B5F6",
    "#90CAF9",
    "#A8D4FA",
    "#BBDEFB",
    "#C6E2FC",
    "#D1E8FD",
    "#DCEEFF",
    "#E5F2FF",
    "#EAF5FF",
    "#EFF8FF",
    "#F4FAFF"
]

bar_colors = (
    ["#E53935"]
    + blue_gradient[:len(chart_data) - 1]
)


# 주요 통계
top_mbti = chart_data.iloc[0]

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "선택한 국가",
        selected_country
    )

with col2:
    st.metric(
        "비율 1위 MBTI",
        top_mbti["MBTI"]
    )

with col3:
    st.metric(
        "1위 비율",
        f'{top_mbti["백분율"]:.2f}%'
    )


# 그래프 제목
st.subheader(
    f"📊 {selected_country}의 MBTI 유형별 비율"
)


# 막대그래프 생성
fig = go.Figure(
    data=[
        go.Bar(
            x=chart_data["MBTI"],
            y=chart_data["백분율"],

            marker=dict(
                color=bar_colors,
                line=dict(
                    color="rgba(0, 0, 0, 0.08)",
                    width=0.5
                )
            ),

            text=[
                f"{value:.2f}%"
                for value in chart_data["백분율"]
            ],

            textposition="outside",

            hovertemplate=(
                "<b>%{x}</b><br>"
                "비율: %{y:.2f}%"
                "<extra></extra>"
            )
        )
    ]
)


# 그래프 디자인
fig.update_layout(
    xaxis_title="MBTI 유형",
    yaxis_title="비율 (%)",

    yaxis=dict(
        rangemode="tozero",
        ticksuffix="%",
        showgrid=True,
        gridcolor="rgba(128,128,128,0.18)"
    ),

    showlegend=False,
    height=520,

    margin=dict(
        l=25,
        r=25,
        t=35,
        b=30
    ),

    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)"
)


# Streamlit 그래프 출력
st.plotly_chart(
    fig,
    use_container_width=True
)


# 순위표
with st.expander("📋 MBTI 비율 순위표 보기"):

    ranking = chart_data[
        ["MBTI", "백분율"]
    ].copy()

    ranking.index = ranking.index + 1
    ranking.index.name = "순위"

    ranking = ranking.rename(
        columns={"백분율": "비율 (%)"}
    )

    ranking["비율 (%)"] = ranking[
        "비율 (%)"
    ].map(lambda x: f"{x:.2f}%")

    st.dataframe(
        ranking,
        use_container_width=True
    )


# 하단 안내
st.caption(
    "※ 빨간색은 비율 1위 MBTI이며, "
    "나머지는 파란색 계열의 그라데이션으로 표시됩니다. "
    "통계는 제공된 CSV 데이터를 기준으로 합니다."
)
