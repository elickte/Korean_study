import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# 페이지 설정
st.set_page_config(page_title="기온 상승과 학업 성취 대시보드", layout="wide")

# 제목
st.title("🌡️ 기온 상승과 학업 성취 대시보드")
st.write("이 대시보드는 기온 변화와 학생 성취 데이터를 시각화합니다.")

# 샘플 데이터 생성
dates = pd.date_range("2020-01-01", periods=50)
temperature = np.random.normal(25, 3, size=50)   # 기온 데이터
scores = np.random.normal(80, 5, size=50)        # 성취도 데이터

df = pd.DataFrame({
    "날짜": dates,
    "기온(℃)": temperature,
    "성취도(점수)": scores
})

# 레이아웃 나누기
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 기온 변화 추이")
    fig_temp = px.line(df, x="날짜", y="기온(℃)", title="일별 기온")
    st.plotly_chart(fig_temp, use_container_width=True)

with col2:
    st.subheader("📊 성취도 변화 추이")
    fig_score = px.line(df, x="날짜", y="성취도(점수)", title="일별 성취도")
    st.plotly_chart(fig_score, use_container_width=True)

# 상관관계 분석
st.subheader("🔗 기온과 성취도의 상관관계")
correlation = df["기온(℃)"].corr(df["성취도(점수)"])
st.write(f"기온과 성취도의 상관계수: **{correlation:.2f}**")

fig_corr = px.scatter(df, x="기온(℃)", y="성취도(점수)", trendline="ols",
                      title="기온 vs 성취도 산점도")
st.plotly_chart(fig_corr, use_container_width=True)
