
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 페이지 설정
st.set_page_config(
    page_title="World MBTI Explorer",
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
        df[col] = pd.to_numeric(
            df[col], errors="coerce"
        )

    df = df.dropna(subset=["Country"])

    return df, mbti_columns


try:
    data, mbti_columns = load_data()

except FileNotFoundError:
    st.error("CSV 파일을 찾을 수 없습니다.")
    st.stop()


# 제목
st.title("🌍 World MBTI Explorer")

st.write(
    "국가별 MBTI 비율과 MBTI 유형별 국가 순위를 "
    "확인할 수 있는 데이터 분석 사이트입니다."
)

st.divider()


# 분석 메뉴
menu = st.radio(
    "📊 분석 메뉴를 선택하세요.",
    [
        "국가별 MBTI 분석",
        "MBTI별 국가 순위"
    ],
    horizontal=True
)

st.divider()


# 색상 그라데이션
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


# ==========================================
# 1. 국가별 MBTI 분석
# ==========================================

if menu == "국가별 MBTI 분석":

    st.header("🌎 국가별 MBTI 비율")

    country_list = sorted(
        data["Country"].unique().tolist()
    )

    selected_country = st.selectbox(
        "국가를 선택하세요.",
        country_list,
        index=(
            country_list.index("South Korea")
            if "South Korea" in country_list
            else 0
        )
    )

    country_data = data[
        data["Country"] == selected_country
    ].iloc[0]

    chart_data = pd.DataFrame({
        "MBTI": mbti_columns,
        "비율": [
            float(country_data[mbti])
            for mbti in mbti_columns
        ]
    })

    chart_data = chart_data.sort_values(
        "비율",
        ascending=False
    ).reset_index(drop=True)

    chart_data["백분율"] = (
        chart_data["비율"] * 100
    )

    # 색상 지정
    colors = (
        ["#E53935"]
        + blue_gradient[:len(chart_data) - 1]
    )

    top = chart_data.iloc[0]

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "선택 국가",
        selected_country
    )

    col2.metric(
        "MBTI 1위",
        top["MBTI"]
    )

    col3.metric(
        "1위 비율",
        f'{top["백분율"]:.2f}%'
    )

    # 그래프
    fig = go.Figure(
        go.Bar(
            x=chart_data["MBTI"],
            y=chart_data["백분율"],
            marker_color=colors,
            text=[
                f"{v:.2f}%"
                for v in chart_data["백분율"]
            ],
            textposition="outside",
            hovertemplate=(
                "<b>%{x}</b><br>"
                "비율: %{y:.2f}%"
                "<extra></extra>"
            )
        )
    )

    fig.update_layout(
        title=f"{selected_country} MBTI 비율",
        xaxis_title="MBTI 유형",
        yaxis_title="비율 (%)",
        yaxis=dict(rangemode="tozero"),
        showlegend=False,
        height=520
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # 순위표
    st.subheader("📋 MBTI 비율 순위")

    ranking = chart_data[
        ["MBTI", "백분율"]
    ].copy()

    ranking.index += 1
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


# ==========================================
# 2. MBTI별 국가 순위
# ==========================================

else:

    st.header("🏆 MBTI별 국가 순위")

    selected_mbti = st.selectbox(
        "MBTI 유형을 선택하세요.",
        mbti_columns
    )

    # 선택한 MBTI의 국가별 비율
    country_ranking = data[
        ["Country", selected_mbti]
    ].copy()

    country_ranking["비율"] = pd.to_numeric(
        country_ranking[selected_mbti],
        errors="coerce"
    )

    country_ranking = country_ranking.dropna(
        subset=["비율"]
    )

    # 비율이 높은 국가부터 정렬
    country_ranking = country_ranking.sort_values(
        "비율",
        ascending=False
    ).reset_index(drop=True)

    country_ranking["순위"] = (
        country_ranking.index + 1
    )

    country_ranking["백분율"] = (
        country_ranking["비율"] * 100
    )

    # 1위 국가 정보
    first = country_ranking.iloc[0]

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "선택 MBTI",
        selected_mbti
    )

    col2.metric(
        "국가 순위 1위",
        first["Country"]
    )

    col3.metric(
        "1위 비율",
        f'{first["백분율"]:.2f}%'
    )

    st.divider()

    # TOP 10 그래프
    st.subheader(
        f"🥇 {selected_mbti} 국가별 TOP 10"
    )

    top10 = country_ranking.head(10)

    # 1위 빨간색, 나머지 파란색
    top10_colors = (
        ["#E53935"]
        + blue_gradient[:9]
    )

    fig = go.Figure(
        go.Bar(
            x=top10["Country"],
            y=top10["백분율"],
            marker_color=top10_colors,
            text=[
                f"{v:.2f}%"
                for v in top10["백분율"]
            ],
            textposition="outside",
            hovertemplate=(
                "<b>%{x}</b><br>"
                "비율: %{y:.2f}%"
                "<extra></extra>"
            )
        )
    )

    fig.update_layout(
        xaxis_title="국가",
        yaxis_title="비율 (%)",
        yaxis=dict(rangemode="tozero"),
        showlegend=False,
        height=500
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # 전체 국가 순위표
    st.subheader(
        f"🌍 {selected_mbti} 전체 국가 순위"
    )

    display_ranking = country_ranking[
        ["순위", "Country", "백분율"]
    ].copy()

    display_ranking = display_ranking.rename(
        columns={
            "Country": "국가",
            "백분율": "비율 (%)"
        }
    )

    display_ranking["비율 (%)"] = (
        display_ranking["비율 (%)"]
        .map(lambda x: f"{x:.2f}%")
    )

    st.dataframe(
        display_ranking,
        use_container_width=True,
        hide_index=True
    )


# 하단 안내
st.divider()

st.caption(
    "🌍 World MBTI Explorer | "
    "국가별 MBTI 통계 데이터 분석"
)

st.caption(
    "※ 모든 순위와 비율은 제공된 CSV 파일을 기준으로 합니다."
)
