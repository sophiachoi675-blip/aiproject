
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from matplotlib.colors import ListedColormap


# ---------------------------------
# 1. 페이지 설정
# ---------------------------------

st.set_page_config(
    page_title="붓꽃 품종 예측 AI",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 붓꽃 품종 예측 프로그램")
st.write(
    "꽃잎의 길이와 너비를 입력하면 "
    "AI가 붓꽃의 품종을 예측합니다."
)

st.divider()


# ---------------------------------
# 2. CSV 데이터 불러오기
# ---------------------------------

@st.cache_data
def load_data():

    # 현재 app.py가 있는 pages 폴더의 상위 폴더
    file_path = Path(__file__).resolve().parent.parent / "csv.csv"

    try:
        df = pd.read_csv(file_path, encoding="cp949")
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding="utf-8-sig")

    return df


try:
    df = load_data()

    required_columns = ["꽃잎길이", "꽃잎너비", "품종"]

    if not all(col in df.columns for col in required_columns):
        st.error("CSV 파일의 컬럼명을 확인해주세요.")
        st.stop()

    df = df.dropna(subset=required_columns).copy()

    if df.empty:
        st.error("분석할 데이터가 없습니다.")
        st.stop()

except FileNotFoundError:
    st.error("상위 폴더에서 csv.csv 파일을 찾을 수 없습니다.")
    st.stop()

except Exception as e:
    st.error(f"데이터 불러오기 오류: {e}")
    st.stop()


# ---------------------------------
# 3. 데이터와 알고리즘 설정
# ---------------------------------

X = df[["꽃잎길이", "꽃잎너비"]]
y = df["품종"]

if y.nunique() < 2:
    st.error("분류를 위해서는 최소 2개 이상의 품종이 필요합니다.")
    st.stop()

# 학습 데이터와 테스트 데이터 분리
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# 랜덤 포레스트 알고리즘
model = RandomForestClassifier(
    n_estimators=200,
    random_state=42
)

# 모델 학습
model.fit(X_train, y_train)

# 테스트 데이터 예측 및 정확도
test_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, test_pred)

# 전체 데이터로 최종 모델 학습
model.fit(X, y)


# ---------------------------------
# 4. 모델 정보 표시
# ---------------------------------

col1, col2, col3 = st.columns(3)

col1.metric("전체 데이터", f"{len(df)}개")
col2.metric("분류 품종", f"{y.nunique()}종")
col3.metric("테스트 정확도", f"{accuracy * 100:.1f}%")

st.caption(
    "테스트 정확도는 전체 데이터 중 20%를 "
    "별도로 분리하여 평가한 결과입니다."
)

st.divider()


# ---------------------------------
# 5. 사용자 입력
# ---------------------------------

st.subheader("📝 꽃잎 크기 입력")

left, right = st.columns(2)

with left:
    petal_length = st.number_input(
        "🌷 꽃잎길이 (cm)",
        min_value=0.1,
        max_value=10.0,
        value=3.0,
        step=0.1
    )

with right:
    petal_width = st.number_input(
        "🌷 꽃잎너비 (cm)",
        min_value=0.1,
        max_value=10.0,
        value=1.0,
        step=0.1
    )


# ---------------------------------
# 6. 품종 예측
# ---------------------------------

input_data = pd.DataFrame(
    [[petal_length, petal_width]],
    columns=["꽃잎길이", "꽃잎너비"]
)

prediction = model.predict(input_data)[0]

probabilities = model.predict_proba(input_data)[0]

class_names = model.classes_

prob_df = pd.DataFrame({
    "품종": class_names,
    "예측 확률(%)": probabilities * 100
})

prob_df = prob_df.sort_values(
    "예측 확률(%)",
    ascending=False
)

# 품종 이름 한글 변환
name_dict = {
    "Iris-setosa": "세토사 (Setosa)",
    "Iris-versicolor": "버시컬러 (Versicolor)",
    "Iris-virginica": "버지니카 (Virginica)"
}

predicted_name = name_dict.get(prediction, prediction)


# ---------------------------------
# 7. 예측 결과 표시
# ---------------------------------

st.divider()

st.subheader("🎯 AI 예측 결과")

st.success(f"예측된 품종은 **{predicted_name}** 입니다!")

best_probability = np.max(probabilities)

st.metric(
    "가장 높은 예측 확률",
    f"{best_probability * 100:.1f}%"
)

st.write(f"입력한 꽃잎길이: **{petal_length} cm**")
st.write(f"입력한 꽃잎너비: **{petal_width} cm**")


# ---------------------------------
# 8. 품종별 예측 확률
# ---------------------------------

st.subheader("📊 품종별 예측 확률")

prob_display = prob_df.copy()

prob_display["품종"] = prob_display["품종"].map(
    lambda x: name_dict.get(x, x)
)

st.bar_chart(
    prob_display.set_index("품종")["예측 확률(%)"],
    y_label="예측 확률 (%)",
    color="#42A5F5"
)


# ---------------------------------
# 9. 그래프 시각화
# ---------------------------------

st.divider()

st.subheader("📈 꽃잎 크기별 품종 분류 시각화")

st.write(
    "초록색 별은 사용자가 입력한 값이며, "
    "배경색은 AI가 분류한 품종 영역입니다."
)

colors = {
    "Iris-setosa": "#4285F4",
    "Iris-versicolor": "#FF9800",
    "Iris-virginica": "#9C27B0"
}

# 그래프 범위
x_min = max(0, X["꽃잎길이"].min() - 0.5)
x_max = X["꽃잎길이"].max() + 0.5

y_min = max(0, X["꽃잎너비"].min() - 0.5)
y_max = X["꽃잎너비"].max() + 0.5

# 예측 영역 계산
xx, yy = np.meshgrid(
    np.arange(x_min, x_max, 0.02),
    np.arange(y_min, y_max, 0.02)
)

grid_data = pd.DataFrame({
    "꽃잎길이": xx.ravel(),
    "꽃잎너비": yy.ravel()
})

Z = model.predict(grid_data)

class_to_num = {
    name: i for i, name in enumerate(model.classes_)
}

Z_num = np.array([
    class_to_num[value] for value in Z
]).reshape(xx.shape)

cmap_background = ListedColormap([
    "#DCEBFA",
    "#FFE8C7",
    "#EBDCF8"
])

fig, ax = plt.subplots(figsize=(11, 7))

# AI 분류 영역
ax.contourf(
    xx,
    yy,
    Z_num,
    levels=np.arange(len(model.classes_) + 1) - 0.5,
    cmap=cmap_background,
    alpha=0.65
)

# 분류 경계선
ax.contour(
    xx,
    yy,
    Z_num,
    levels=np.arange(len(model.classes_) - 1) + 0.5,
    colors="gray",
    linewidths=1
)

# 기존 데이터 표시
for species in model.classes_:

    subset = df[df["품종"] == species]

    ax.scatter(
        subset["꽃잎길이"],
        subset["꽃잎너비"],
        color=colors.get(species, "#808080"),
        label=name_dict.get(species, species),
        s=55,
        alpha=0.8,
        edgecolors="white"
    )

# 사용자 입력값: 초록색 별
ax.scatter(
    petal_length,
    petal_width,
    color="#00C853",
    marker="*",
    s=400,
    edgecolors="black",
    linewidths=1.2,
    label="내가 입력한 값",
    zorder=10
)

ax.annotate(
    f"입력값 ({petal_length}, {petal_width})",
    (petal_length, petal_width),
    xytext=(12, 12),
    textcoords="offset points",
    fontsize=10,
    fontweight="bold"
)

ax.set_xlabel("꽃잎길이 (cm)", fontsize=12)
ax.set_ylabel("꽃잎너비 (cm)", fontsize=12)

ax.set_title(
    "Iris Species Classification - Random Forest",
    fontsize=14
)

ax.legend(loc="best")
ax.grid(alpha=0.2)

st.pyplot(fig, use_container_width=True)

plt.close(fig)


# ---------------------------------
# 10. 예측 이유 설명
# ---------------------------------

st.divider()

st.subheader("🔍 AI가 이 품종으로 예측한 이유")

st.write(
    f"사용자가 입력한 꽃잎길이는 {petal_length}cm, "
    f"꽃잎너비는 {petal_width}cm입니다."
)

st.write(
    f"AI는 두 가지 특징을 학습 데이터의 "
    f"품종별 패턴과 비교했습니다."
)

st.write(
    f"그 결과 {predicted_name}의 예측 확률이 "
    f"가장 높게 나타났습니다."
)

# 의사결정나무별 예측 결과
tree_predictions = np.array([
    tree.predict(input_data)[0]
    for tree in model.estimators_
])

vote_counts = pd.Series(tree_predictions).value_counts()

vote_df = pd.DataFrame({
    "품종": [
        name_dict.get(name, name)
        for name in model.classes_
    ],
    "투표한 나무 수": [
        int(vote_counts.get(name, 0))
        for name in model.classes_
    ]
})

st.write("🌳 200개 의사결정나무의 개별 예측 결과")

st.dataframe(
    vote_df,
    use_container_width=True,
    hide_index=True
)

st.info(
    "초록색 별이 위치한 배경색은 AI의 분류 영역을 "
    "나타냅니다. 예측 확률과 나무별 투표 결과를 "
    "함께 확인하면 분류 결과를 더 잘 이해할 수 있습니다."
)

st.divider()

st.caption(
    "Iris 데이터와 Random Forest 알고리즘을 활용한 "
    "머신러닝 품종 분류 프로그램입니다."
)


