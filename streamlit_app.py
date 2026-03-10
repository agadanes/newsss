import streamlit as st
import feedparser
import yfinance as yf
import pandas as pd

# 1. 페이지 설정 (아이폰 11 최적화)
st.set_page_config(page_title="아침 루틴", layout="wide")

# 2. 아이폰용 초슬림 디자인 (CSS)
st.markdown("""
    <style>
    /* 여백 최소화 */
    .main .block-container {
        padding-top: 1rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }
    /* 3x3 금융 격자 디자인 */
    [data-testid="stMetric"] {
        background-color: #f8f9fa;
        padding: 5px !important;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        height: 75px !important; 
        display: flex;
        flex-direction: column;
        justify-content: center;
        text-align: center;
    }
    [data-testid="stMetricLabel"] { font-size: 0.65rem !important; color: #555; }
    [data-testid="stMetricValue"] { font-size: 0.95rem !important; font-weight: 800 !important; }
    [data-testid="stMetricDelta"] { font-size: 0.6rem !important; }
    /* 뉴스 리스트 가독성 */
    .news-item { font-size: 0.9rem; margin-bottom: 8px; line-height: 1.3; }
    </style>
    """, unsafe_allow_html=True)

st.title("☀️ 나의 아침 핵심 루틴")

# 3. 뉴스 및 금융 탭 구성
tab1, tab2, tab3, tab4, tab5 = st.tabs(["사회", "경제", "세계", "USA", "금융9"])

def display_news(url):
    feed = feedparser.parse(url)
    if not feed.entries:
        st.write("뉴스를 불러오는 중...")
    else:
        for entry in feed.entries[:5]:
            st.markdown(f"<p class='news-item'>• <a href='{entry.link}' target='_blank' style='text-decoration:none; color:black;'><b>{entry.title}</b></a></p>", unsafe_allow_html=True)
            st.divider()

# 뉴스 탭 연결
with tab1: display_news("https://www.chosun.com/arc/outboundfeeds/rss/category/national/?outputType=xml")
with tab2: display_news("https://www.mk.co.kr/rss/30100041/")
with tab3: display_news("https://www.hani.co.kr/rss/international/")
with tab4: display_news("http://rss.cnn.com/rss/edition.rss")

# 4. 금융 9개 격자 (실시간 지수)
with tab5:
    st.subheader("📊 실시간 지수 (3x3)")
    tickers = {
        "KOSPI": "^KS11", "나스닥": "^IXIC", "S&P500": "^GSPC",
        "비트코인": "BTC-USD", "이더리움": "ETH-USD", "달러환율": "USDKRW=X",
        "금 (Gold)": "GC=F", "은 (Silver)": "SI=F", "구리": "HG=F"
    }

    @st.cache_data(ttl=60)
    def get_price(ticker):
        try:
            # yfinance 최신 안정화 방식 (download 사용)
            data = yf.download(ticker, period="2d", interval="1d", progress=False)
            if not data.empty:
                curr = float(data['Close'].iloc[-1])
                prev = float(data['Close'].iloc[-2])
                return curr, curr - prev
        except: pass
        return None, None

    items = list(tickers.items())
    
    # 3개씩 끊어서 가로로 배치 (3열 x 3행)
    for i in range(0, 9, 3):
        col1, col2, col3 = st.columns(3)
        cols = [col1, col2, col3]
        for j in range(3):
            with cols[j]:
                name, tick = items[i+j]
                val, diff = get_price(tick)
                if val is not None:
                    # 환율/원자재는 소수점 1자리, 지수는 정수
                    fmt = "{:,.1f}" if "USD" in tick or "=" in tick or "F" in tick else "{:,.0f}"
                    pct = (diff / (val - diff)) * 100 if (val - diff) != 0 else 0
                    st.metric(label=name, value=fmt.format(val), delta=f"{pct:.1f}%")
                else:
                    st.metric(label=name, value="연결중", delta="0%")
