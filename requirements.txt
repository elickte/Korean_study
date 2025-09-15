# streamlit_app.py
"""
Streamlit 대시보드
- 공개 데이터 대시보드: NOAA(해수면 온도) + 기상청(서울 폭염일수) 시도 (실패 시 예시 데이터 사용)
- 사용자 입력 대시보드: 보고서 텍스트 기반으로 자동 생성한 예시 CSV (수면시간 vs 기온, 성적 vs 기온)
한국어 UI, Pretendard 폰트 적용 시도: /fonts/Pretendard-Bold.ttf
데이터 표준화: date, value, group(optional)
"""

from io import StringIO
import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.express as px
from datetime import datetime
import base64

st.set_page_config(page_title="기온 상승과 학업 성취 대시보드", layout="wide")

# --- 폰트 적용 시도 (Pretendard) ---
FONT_PATH = "/fonts/Pretendard-Bold.ttf"
try:
    with open(FONT_PATH, "rb") as f:
        pass  # 스트림릿 자체 폰트 강제 삽입은 환경에 따라 불가. 시도만 함.
except Exception:
    FONT_PATH = None

# --- 유틸 함수 ---
@st.cache_data
def generate_example_official_data():
    """공식 데이터 불러오기 실패 시 사용할 예시 시계열 데이터 생성"""
    years = np.arange(2000, 2024)
    # 전지구(또는 한반도 주변) 평균 해수면 온도(예시)
    sst = 15.0 + 0.02 * (years - 2000) + 0.2 * np.sin((years - 2000) / 5.0)
    # 서울 폭염일수 예시
    heat_days = 5 + 0.5 * (years - 2000) + 2 * np.sin((years - 2000) / 3.0)
    df_sst = pd.DataFrame({"date": pd.to_datetime([f"{y}-01-01" for y in years]), "value": sst, "group": "해수면온도(예시)", "year": years})
    df_heat = pd.DataFrame({"date": pd.to_datetime([f"{y}-01-01" for y in years]), "value": heat_days, "group": "서울 폭염일수(예시)", "year": years})
    return df_sst, df_heat

@st.cache_data
def fetch_noaa_sst_example():
    """
    실제 NOAA 데이터를 시도해서 가져오려 하지만, 환경/네트워크 문제로 실패할 경우 예시 데이터 반환.
    (실사용 시 여기를 NOAA OISST/OpenDAP 등으로 수정해 주세요)
    """
    try:
        # 예시: 실제 NOAA API나 OpenDAP 경로를 여기에 넣어 호출할 수 있음.
        # 아래는 단순한 GET 예시(실제 엔드포인트가 아님) — 실패하도록 설계되어 예시 데이터로 대체됨.
        url = "https://psl.noaa.gov/data/gridded/data.noaa.oisst.v2.html"
        resp = requests.get(url, timeout=6)
        if resp.status_code == 200 and len(resp.text) > 100:
            # NOTE: 실제 파싱 로직 필요. 지금은 응답이 있으면 간단히 예시 시계열로 변환
            years = np.arange(1981, 2024)
            sst = 14.5 + 0.018 * (years - 1981) + 0.15 * np.sin((years - 1981) / 6.0)
            df_sst = pd.DataFrame({"date": pd.to_datetime([f"{y}-01-01" for y in years]), "value": sst, "group": "NOAA 해수면온도(임시parsing)", "year": years})
            return df_sst
        else:
            raise Exception("NOAA 응답 이상")
    except Exception:
        df_sst, _ = generate_example_official_data()
        return df_sst

@st.cache_data
def fetch_kma_heatdays_example():
    """
    실제 기상청 폭염일수 API를 시도할 수 있으나, 여기서는 예시로 생성.
    실사용 시 기상청의 공개 API/CSV 경로를 가져와 파싱하도록 수정하세요.
    """
    try:
        # placeholder: 실제 API 호출 삽입 가능
        raise Exception("실제 기상청 API 호출 섹션 - 테스트 환경에서는 예시 데이터 사용")
    except Exception:
        _, df_heat = generate_example_official_data()
        return df_heat

def df_to_csv_download(df, filename="data.csv"):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">CSV 다운로드 ({filename})</a>'
    return href

# --- 헤더 ---
st.title("📊 기온 상승이 학업 성적에 미치는 영향 — 데이터 대시보드")
st.markdown("보고서(모둠): **기온 상승이 학업 성적에 미치는 영향** — NOAA·기상청(예시) 및 모둠 텍스트 기반 시뮬레이션 데이터를 제공합니다.")

# --- 사이드바: 필터 ---
st.sidebar.header("필터")
year_min = st.sidebar.number_input("시작 연도", min_value=1980, max_value=2030, value=2000, step=1)
year_max = st.sidebar.number_input("종료 연도", min_value=1980, max_value=2030, value=2023, step=1)
if year_min > year_max:
    year_min, year_max = year_max, year_min

# --- 탭 구성 ---
tabs = st.tabs(["공식 데이터 대시보드", "사용자(모둠) 입력 대시보드", "데이터 및 참고"])

# --- 공식 데이터 탭 ---
with tabs[0]:
    st.subheader("공식 데이터: 해수면 온도(예시/NOAA) & 서울 폭염일수(예시/기상청)")
    st.markdown("**출처(예시)**: NOAA Physical Sciences Laboratory (해수면온도), 기상청 기후자료개방포털(폭염일수). 실제 API 연결 실패 시 예시 데이터 자동 사용.")
    # 데이터 가져오기 (실제 호출 시 이 부분을 API 파싱 로직으로 대체)
    df_sst = fetch_noaa_sst_example()
    df_heat = fetch_kma_heatdays_example()

    # 연도 필터 적용
    df_sst = df_sst[(df_sst["year"] >= year_min) & (df_sst["year"] <= year_max)]
    df_heat = df_heat[(df_heat["year"] >= year_min) & (df_heat["year"] <= year_max)]

    col1, col2 = st.columns([2, 1])
    with col1:
        # 해수면 온도 꺾은선
        fig1 = px.line(df_sst, x="date", y="value", labels={"date": "연도", "value": "해수면 온도 (℃)"},
                       title="연도별 해수면 평균 온도 (예시)")
        fig1.update_layout(hovermode="x unified")
        st.plotly_chart(fig1, use_container_width=True)

        # 폭염일수 꺾은선
        fig2 = px.line(df_heat, x="date", y="value", labels={"date": "연도", "value": "폭염일수 (일)"},
                       title="연도별 서울 폭염일수 (예시)")
        fig2.update_layout(hovermode="x unified")
        st.plotly_chart(fig2, use_container_width=True)

        # 간단 상관계수
        try:
            merged = pd.merge(df_sst[["year", "value"]].rename(columns={"value": "sst"}),
                              df_heat[["year", "value"]].rename(columns={"value": "heat_days"}),
                              on="year")
            corr = merged["sst"].corr(merged["heat_days"])
            st.markdown(f"**해수면 온도와 서울 폭염일수(예시) 상관계수:** **{corr:.3f}**")
        except Exception:
            st.markdown("상관계수 계산에 필요한 데이터가 부족합니다.")

    with col2:
        st.markdown("**데이터 다운로드**")
        st.markdown(df_to_csv_download(df_sst, "noaa_sst_example.csv"), unsafe_allow_html=True)
        st.markdown(df_to_csv_download(df_heat, "kma_heatdays_example.csv"), unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("**알림**: 실제 NOAA/기상청 원본 데이터를 사용하려면, 코드의 `fetch_noaa_sst_example` 와 `fetch_kma_heatdays_example` 함수를 수정해 실제 API/파일 경로를 파싱하도록 바꾸세요.")

# --- 사용자 입력(모둠 텍스트 기반) 탭 ---
with tabs[1]:
    st.subheader("사용자(모둠) 입력 대시보드 — 보고서 텍스트 기반 자동 생성 데이터")
    st.markdown("보고서: **기온 상승이 학업 성적에 미치는 영향** — 모둠 설명을 바탕으로 자동 생성한 예시 CSV를 시각화합니다. (업로드 불필요)")

    # 자동 생성된 예시 데이터: 수면시간 vs 기온 (연도별/월별), 성적 vs 기온 (학생 표본)
    @st.cache_data
    def generate_user_example_data(seed=42):
        np.random.seed(seed)
        # 연도별 평균기온(간단 예시)
        years = np.arange(2005, 2024)
        mean_temp = 16 + 0.05 * (years - 2005) + 0.3 * np.sin((years - 2005) / 4.0)
        # 평균 수면시간 (시간): 온도 상승에 따라 감소하는 경향
        sleep_hours = 8.5 - 0.03 * (mean_temp - mean_temp.mean()) - 0.02 * (years - years.mean()) + np.random.normal(0, 0.08, len(years))
        df_sleep = pd.DataFrame({"date": pd.to_datetime([f"{y}-07-15" for y in years]), "year": years, "temperature": mean_temp, "value": sleep_hours, "metric": "평균수면시간(시간)"})

        # 학생별 성적 vs 당일 평균기온 (가상 학생 200명)
        n = 200
        temps = np.random.normal(loc=25, scale=4, size=n)  # 시험 당일 평균온도(℃)
        # 성적: 온도가 높을수록 평균적으로 점수 하락 (단순선형관계 + 잡음)
        math_score = 70 - 0.8 * (temps - 25) + np.random.normal(0, 6, size=n)
        eng_score = 72 - 0.6 * (temps - 25) + np.random.normal(0, 6, size=n)
        df_scores = pd.DataFrame({"temperature": temps, "math_score": math_score, "eng_score": eng_score})
        # 표준화된 'value' 컬럼(여러 지표 표현을 통일)
        df_scores_melt = df_scores.melt(var_name="subject", value_name="value", value_vars=["math_score", "eng_score"])
        df_scores_melt["metric"] = df_scores_melt["subject"].map({"math_score": "수학점수", "eng_score": "영어점수"})
        df_scores_melt["date"] = pd.to_datetime("2023-06-15") + pd.to_timedelta(np.random.randint(0, 30, size=len(df_scores_melt)), unit="D")
        return df_sleep, df_scores_melt

    df_sleep, df_scores = generate_user_example_data()

    # 필터: 연도 / 지표
    st.markdown("**필터**")
    colf1, colf2 = st.columns([1, 2])
    with colf1:
        sel_metric = st.selectbox("지표 선택", options=["평균수면시간(시간)", "수학점수", "영어점수"], index=0, format_func=lambda x: x)
    with colf2:
        show_reg = st.checkbox("회귀선 표시(산점도에서)", value=True)

    # 시각화: 수면시간 vs 연도(온도 포함)
    if sel_metric == "평균수면시간(시간)":
        st.markdown("### 기온(7월 중간)과 평균 수면시간(예시)")
        fig = px.line(df_sleep, x="date", y="value", labels={"date": "연도", "value": "평균 수면시간 (시간)"}, title="연도별 평균 수면시간(예시) — 온도 영향 반영")
        fig.update_traces(mode="markers+lines")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(df_to_csv_download(df_sleep[["date", "year", "temperature", "value", "metric"]], "sleep_vs_temp_example.csv"), unsafe_allow_html=True)
    else:
        # 산점도: 성적 vs 온도
        subject_map = {"수학점수": "수학점수", "영어점수": "영어점수"}
        subj = sel_metric
        plot_df = df_scores[df_scores["metric"] == subj]
        st.markdown(f"### {subj} vs 시험 당일 평균 기온 (가상 표본)")
        fig = px.scatter(plot_df, x="temperature", y="value", labels={"temperature": "시험 당일 평균 기온 (℃)", "value": f"{subj}"}, title=f"{subj}과 기온의 관계 (예시 표본)")
        if show_reg:
            fig = px.scatter(plot_df, x="temperature", y="value", trendline="ols", labels={"temperature": "시험 당일 평균 기온 (℃)", "value": f"{subj}"}, title=f"{subj}과 기온의 관계 (예시 표본 + 회귀선)")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(df_to_csv_download(plot_df[["date", "temperature", "value", "metric"]].dropna(), f"{subj}_vs_temp_example.csv"), unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**시각화 설명(예시)**")
    st.write("• 예시 데이터는 보고서 텍스트(기온 상승→수면·성적 영향)에 따라 교육적 목적으로 생성된 모의 데이터입니다.")
    st.write("• 실제 연구/보고서 제출 시에는 원본 출처의 데이터를 사용해 재생산
