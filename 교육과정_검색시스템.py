import streamlit as st
import pandas as pd
from pathlib import Path

# ==============================
# 기본 설정
# ==============================
st.set_page_config(
    page_title="교육과정 검색",
    page_icon="📚",
    layout="wide"
)

st.title("📚 국가평생교육진흥원 AI·D 집중과정")
st.caption("AI·D 집중과정을 검색하고 확인할 수 있습니다.")

# ==============================
# AI·D 집중과정 안내 이미지
# ==============================
IMAGE_FILE = Path(__file__).parent / "AID.jpg"

if IMAGE_FILE.exists():
    st.image(
        str(IMAGE_FILE),
        use_container_width=True
    )

# ==============================
# 데이터 불러오기
# ==============================
CSV_FILE = Path(__file__).parent / "교육과정.csv"

@st.cache_data
def load_data():
    # 한글 CSV 호환성을 위해 UTF-8-SIG 우선 사용
    try:
        data = pd.read_csv(CSV_FILE, encoding="utf-8-sig")
    except UnicodeDecodeError:
        data = pd.read_csv(CSV_FILE, encoding="cp949")

    data.columns = [str(c).strip() for c in data.columns]

    # 모든 컬럼을 문자열로 처리
    for col in data.columns:
        data[col] = data[col].fillna("").astype(str).str.strip()

    return data

df = load_data()

# ==============================
# 필요한 컬럼 확인
# ==============================
required_columns = [
    "구분",
    "학교",
    "직군",
    "교육과정명",
    "세부교육과정명",
    "운영일정",
    "수강 정보"
]

missing = [col for col in required_columns if col not in df.columns]

if missing:
    st.error("CSV 파일에서 다음 컬럼을 찾을 수 없습니다.")
    st.write(missing)
    st.write("현재 CSV 컬럼:", list(df.columns))
    st.stop()

# ==============================
# 사이드바 검색 조건
# ==============================
st.sidebar.header("🔎 검색 조건")

keyword = st.sidebar.text_input(
    "키워드 검색",
    placeholder="교육과정명, 학교, 직군 등을 입력하세요"
)

category_options = ["전체"] + sorted(
    [x for x in df["구분"].unique() if x]
)
school_options = ["전체"] + sorted(
    [x for x in df["학교"].unique() if x]
)
job_options = ["전체"] + sorted(
    [x for x in df["직군"].unique() if x]
)

category = st.sidebar.selectbox("구분", category_options)
school = st.sidebar.selectbox("학교", school_options)
job = st.sidebar.selectbox("직군", job_options)

# ==============================
# 데이터 필터링
# ==============================
result = df.copy()

if keyword:
    search_columns = [
        "구분",
        "학교",
        "직군",
        "교육과정명",
        "세부교육과정명",
        "운영일정"
    ]

    mask = pd.Series(False, index=result.index)

    for col in search_columns:
        mask = mask | result[col].str.contains(
            keyword,
            case=False,
            na=False,
            regex=False
        )

    result = result[mask]

if category != "전체":
    result = result[result["구분"] == category]

if school != "전체":
    result = result[result["학교"] == school]

if job != "전체":
    result = result[result["직군"] == job]

# ==============================
# 상단 통계
# ==============================
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("전체 교육과정", f"{len(df):,}개")

with col2:
    st.metric("검색 결과", f"{len(result):,}개")

with col3:
    st.metric("운영 학교", f"{df['학교'].nunique():,}개")

st.markdown("---")

# ==============================
# 검색 결과
# ==============================
st.subheader(f"📋 검색 결과 ({len(result):,}개)")

if result.empty:
    st.warning("검색 조건에 맞는 교육과정이 없습니다.")
else:
    # 결과를 카드 형태로 표시
    for idx, row in result.reset_index(drop=True).iterrows():

        with st.container(border=True):
            top_col1, top_col2 = st.columns([5, 1])

            with top_col1:
                st.markdown(
                    f"### {row['교육과정명']}"
                )

                if row["세부교육과정명"]:
                    st.markdown(
                        f"**세부교육과정:** {row['세부교육과정명']}"
                    )

            with top_col2:
                st.markdown(f"**{row['구분']}**")

            info1, info2, info3 = st.columns(3)

            with info1:
                st.markdown(f"🏫 **학교**  \n{row['학교']}")

            with info2:
                st.markdown(f"👤 **직군**  \n{row['직군']}")

            with info3:
                st.markdown(f"📅 **운영일정**  \n{row['운영일정']}")

            course_link = str(row["수강 정보"]).strip()

            if course_link and course_link.lower() not in ["nan", "none"]:
                st.link_button(
                    "🔗 교육과정 상세보기",
                    course_link,
                    width="stretch"
                )
            else:
                st.button(
                    "준비 중입니다",
                    disabled=True,
                    width="stretch",
                    key=f"preparing_{idx}"
                )

# ==============================
# 데이터 다운로드
# ==============================
st.markdown("---")

st.subheader("📥 검색 결과 다운로드")

download_data = result.to_csv(
    index=False,
    encoding="utf-8-sig"
)

st.download_button(
    label="CSV 다운로드",
    data=download_data,
    file_name="교육과정_검색결과.csv",
    mime="text/csv"
)

# ==============================
# 원본 데이터 보기
# ==============================
with st.expander("📊 원본 데이터 보기"):
    st.dataframe(
        df,
        width="stretch",
        hide_index=True
    )
