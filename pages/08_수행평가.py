
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# --------------------------------
# 1. 페이지 설정
# --------------------------------

st.set_page_config(
    page_title="지역별 범죄 통계 분석",
    page_icon="🚨",
    layout="wide"
)

# --------------------------------
# 2. CSV 파일 경로
# --------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

CSV_FILE = BASE_DIR / "경찰청_범죄 발생 지역별 통계_20251231.csv"


# --------------------------------
# 3. 데이터 불러오기
# --------------------------------

@st.cache_data
def load_data():

    try:
        df = pd.read_csv(CSV_FILE, encoding="cp949")
    except UnicodeDecodeError:
        df = pd.read_csv(CSV_FILE, encoding="utf-8-sig")

    df.columns = df.columns.str.strip()

    for col in df.columns[2:]:
        df[col] = pd.to_numeric(
            df[col], errors="coerce"
        ).fillna(0)

    return df


try:
    df = load_data()

except FileNotFoundError:
    st.error("CSV 파일을 찾을 수 없습니다.")
    st.stop()

except Exception as e:
    st.error(f"데이터 오류: {e}")
    st.stop()


# --------------------------------
# 4. 데이터 구조 확인
# --------------------------------

required_columns = ["범죄대분류", "범죄중분류"]

if not all(col in df.columns for col in required_columns):
    st.error("CSV 파일의 범죄 분류 열을 확인해 주세요.")
    st.stop()

# 기존 지역 선택 기능 유지
region_columns = df.columns[2:].tolist()

# 전국 순위에서는 외국 국적 항목 제외
domestic_regions = [
    col for col in region_columns
    if not col.startswith("외국 ")
]

if not region_columns or not domestic_regions:
    st.error("지역 데이터가 없습니다.")
    st.stop()


# --------------------------------
# 5. 제목
# --------------------------------

st.title("🚨 지역별 범죄 통계 분석")

st.write(
    "경찰청 데이터를 활용하여 지역별 범죄 발생 현황과 "
    "범죄 종류별 비율을 분석합니다."
)

st.divider()


# --------------------------------
# 6. 지역 및 범죄 종류 선택
# --------------------------------

col1, col2 = st.columns(2)

with col1:
    selected_region = st.selectbox(
        "📍 분석할 지역을 선택하세요.",
        region_columns
    )

with col2:
    crime_categories = sorted(
        df["범죄대분류"].dropna().unique().tolist()
    )

    category_options = ["전체 범죄대분류"] + crime_categories

    selected_category = st.selectbox(
        "🔎 분석할 범죄 종류를 선택하세요.",
        category_options
    )


# --------------------------------
# 7. 선택 지역 데이터 분석
# --------------------------------

if selected_category == "전체 범죄대분류":

    crime_data = df.groupby(
        "범죄대분류",
        as_index=False
    )[selected_region].sum()

    crime_data = crime_data.rename(
        columns={
            "범죄대분류": "범죄종류",
            selected_region: "발생건수"
        }
    )

    analysis_title = "범죄대분류별 발생 비율"

else:

    filtered_df = df[
        df["범죄대분류"] == selected_category
    ]

    crime_data = filtered_df.groupby(
        "범죄중분류",
        as_index=False
    )[selected_region].sum()

    crime_data = crime_data.rename(
        columns={
            "범죄중분류": "범죄종류",
            selected_region: "발생건수"
        }
    )

    analysis_title = f"{selected_category} 세부 범죄 발생 비율"


# --------------------------------
# 8. 비율 계산
# --------------------------------

crime_data = crime_data[
    crime_data["발생건수"] > 0
].copy()

if crime_data.empty:
    st.warning("선택한 조건에 해당하는 데이터가 없습니다.")
    st.stop()

total_crimes = crime_data["발생건수"].sum()

crime_data["비율"] = (
    crime_data["발생건수"] / total_crimes * 100
)

crime_data = crime_data.sort_values(
    "발생건수",
    ascending=False
).reset_index(drop=True)

crime_data["순위"] = range(
    1, len(crime_data) + 1
)


# --------------------------------
# 9. 주요 통계
# --------------------------------

st.subheader(f"📌 {selected_region} 분석 결과")

col1, col2, col3 = st.columns(3)

col1.metric(
    "총 발생 건수",
    f"{total_crimes:,.0f}건"
)

col2.metric(
    "분석 범죄 종류",
    f"{len(crime_data)}개"
)

col3.metric(
    "발생 비율 1위",
    crime_data.iloc[0]["범죄종류"]
)

st.divider()


# --------------------------------
# 10. 그래프 색상 설정
# --------------------------------

blue_gradient = [
    "#2563EB",
    "#3B82F6",
    "#60A5FA",
    "#7CB5F8",
    "#93C5FD",
    "#B0D0FC",
    "#BFDBFE",
    "#D3E5FF",
    "#DBEAFE"
]

colors = ["#EF4444"]

for i in range(1, len(crime_data)):
    color_index = min(
        i - 1,
        len(blue_gradient) - 1
    )

    colors.append(blue_gradient[color_index])


# --------------------------------
# 11. 기존 범죄 비율 그래프
# --------------------------------

st.subheader(f"📊 {analysis_title}")

fig = go.Figure()

fig.add_trace(
    go.Bar(
        x=crime_data["비율"],
        y=crime_data["범죄종류"],
        orientation="h",

        marker=dict(
            color=colors,
            line=dict(width=0)
        ),

        text=[
            f"{value:.2f}%"
            for value in crime_data["비율"]
        ],

        textposition="outside",

        customdata=crime_data[
            ["발생건수", "순위"]
        ].values,

        hovertemplate=
        "<b>%{y}</b><br>" +
        "발생 건수: %{customdata[0]:,.0f}건<br>" +
        "발생 비율: %{x:.2f}%<br>" +
        "순위: %{customdata[1]}위" +
        "<extra></extra>"
    )
)

fig.update_layout(
    template="plotly_white",

    title=dict(
        text=f"{selected_region} | {analysis_title}",
        x=0.02
    ),

    height=max(
        430,
        len(crime_data) * 43
    ),

    xaxis_title="발생 비율 (%)",
    yaxis_title="범죄 종류",

    showlegend=False,
    bargap=0.35,

    margin=dict(
        l=30,
        r=80,
        t=80,
        b=50
    ),

    font=dict(
        family="Arial",
        size=13
    )
)

fig.update_xaxes(
    ticksuffix="%",
    showgrid=True,
    gridcolor="#EEEEEE"
)

fig.update_yaxes(
    categoryorder="array",
    categoryarray=crime_data["범죄종류"].tolist(),
    autorange="reversed",
    showgrid=False
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# --------------------------------
# 12. 기존 범죄 발생 순위 TOP 5
# --------------------------------

st.divider()

st.subheader("🏆 범죄 발생 순위 TOP 5")

top5 = crime_data.head(5).copy()

top5_display = top5[
    ["순위", "범죄종류", "발생건수", "비율"]
].copy()

top5_display["발생건수"] = top5_display[
    "발생건수"
].map(lambda x: f"{x:,.0f}건")

top5_display["비율"] = top5_display[
    "비율"
].map(lambda x: f"{x:.2f}%")

st.dataframe(
    top5_display,
    use_container_width=True,
    hide_index=True
)


# --------------------------------
# 13. 전국 지역별 범죄 발생 TOP 10
# --------------------------------

st.divider()

st.subheader("🌎 전국 지역별 범죄 발생 TOP 10")

# 선택한 범죄 종류에 따라 전국 발생 건수 계산

if selected_category == "전체 범죄대분류":

    ranking_series = df[
        domestic_regions
    ].sum()

else:

    ranking_series = df[
        df["범죄대분류"] == selected_category
    ][domestic_regions].sum()


# 지역별 발생 건수 정렬
ranking_series = ranking_series.sort_values(
    ascending=False
)

ranking_data = ranking_series.head(10).reset_index()

ranking_data.columns = [
    "지역",
    "발생건수"
]

ranking_data["순위"] = range(
    1, len(ranking_data) + 1
)


# TOP 10 색상 설정
rank_colors = ["#EF4444"]

rank_blue = [
    "#2563EB",
    "#3B82F6",
    "#60A5FA",
    "#7CB5F8",
    "#93C5FD",
    "#B0D0FC",
    "#BFDBFE",
    "#D3E5FF",
    "#DBEAFE"
]

for i in range(1, len(ranking_data)):
    rank_colors.append(
        rank_blue[min(i - 1, len(rank_blue) - 1)]
    )


# 전국 순위 그래프
rank_fig = go.Figure()

rank_fig.add_trace(
    go.Bar(
        x=ranking_data["발생건수"],
        y=ranking_data["지역"],
        orientation="h",

        marker_color=rank_colors,

        text=[
            f"{v:,.0f}건"
            for v in ranking_data["발생건수"]
        ],

        textposition="outside",

        hovertemplate=
        "<b>%{y}</b><br>" +
        "발생 건수: %{x:,.0f}건" +
        "<extra></extra>"
    )
)

rank_fig.update_layout(
    template="plotly_white",

    title="전국 지역별 범죄 발생 건수 순위",

    height=520,

    xaxis_title="범죄 발생 건수",
    yaxis_title="지역",

    showlegend=False,

    margin=dict(
        l=30,
        r=90,
        t=70,
        b=50
    )
)

rank_fig.update_yaxes(
    autorange="reversed",
    showgrid=False
)

rank_fig.update_xaxes(
    showgrid=True,
    gridcolor="#EEEEEE"
)

st.plotly_chart(
    rank_fig,
    use_container_width=True
)


# --------------------------------
# 14. 데이터 분석 의미 (최대 3줄)
# --------------------------------

st.divider()

st.subheader("💡 데이터 분석 의미")

# 전국 1위 지역
top_region = ranking_data.iloc[0]["지역"]
top_region_count = ranking_data.iloc[0]["발생건수"]

# 선택 지역의 전국 순위
selected_region_rank = (
    ranking_series.rank(
        ascending=False,
        method="min"
    )
)

# 선택 지역의 가장 많이 발생한 범죄
top_crime = crime_data.iloc[0]["범죄종류"]
top_crime_count = crime_data.iloc[0]["발생건수"]
top_crime_ratio = crime_data.iloc[0]["비율"]

# 분석 문장 생성
insights = []

insights.append(
    f"① 전국에서 범죄 발생 건수가 가장 많은 지역은 "
    f"**{top_region}**이며, 총 **{top_region_count:,.0f}건**입니다."
)

if selected_region in domestic_regions:

    region_rank = int(
        selected_region_rank[selected_region]
    )

    insights.append(
        f"② **{selected_region}**은 전국 지역 중 "
        f"범죄 발생 건수 **{region_rank}위**입니다."
    )

else:

    insights.append(
        f"② 외국 국적별 통계는 국내 지역 순위에서 제외됩니다."
    )

insights.append(
    f"③ {selected_region}에서 가장 많이 발생한 범죄는 "
    f"**{top_crime}**이며, 선택한 분석 범위의 "
    f"**{top_crime_ratio:.2f}%**를 차지합니다."
)

st.info("\n\n".join(insights))


# --------------------------------
# 15. 기존 상세 데이터 표
# --------------------------------

st.divider()

st.subheader("📋 범죄 종류별 상세 데이터")

display_data = crime_data[
    ["순위", "범죄종류", "발생건수", "비율"]
].copy()

display_data["발생건수"] = display_data[
    "발생건수"
].map(lambda x: f"{x:,.0f}건")

display_data["비율"] = display_data[
    "비율"
].map(lambda x: f"{x:.2f}%")

st.dataframe(
    display_data,
    use_container_width=True,
    hide_index=True
)


# --------------------------------
# 16. 기존 CSV 다운로드
# --------------------------------

st.divider()

download_data = crime_data[
    ["순위", "범죄종류", "발생건수", "비율"]
]

csv_data = download_data.to_csv(
    index=False,
    encoding="utf-8-sig"
)

st.download_button(
    label="📥 분석 데이터 다운로드",
    data=csv_data,
    file_name="지역별_범죄통계_분석.csv",
    mime="text/csv"
)


# --------------------------------
# 17. 안내 문구
# --------------------------------

st.divider()

st.caption(
    "자료 출처: 경찰청 범죄 발생 지역별 통계 (2025년 기준)"
)

st.caption(
    "※ 범죄 발생 건수는 인구 규모를 반영하지 않은 단순 집계입니다. "
    "지역별 안전도나 인구 대비 범죄 위험도를 의미하지 않습니다."
)
