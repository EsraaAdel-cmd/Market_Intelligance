import os
import streamlit as st
import pandas as pd
import plotly.express as px
import requests

st.set_page_config(page_title="Market Intelligence", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
* { font-family: 'Inter', sans-serif !important; }
.stApp { background: #08080f; }
section[data-testid="stSidebar"] { background: #0c0c14 !important; border-right: 1px solid #161622; min-width: 210px !important; max-width: 210px !important; }
.sidebar-brand { padding: 20px 0 18px; border-bottom: 1px solid #161622; margin-bottom: 22px; }
.sidebar-brand-title { font-size: 13px; font-weight: 700; color: #f1f5f9; }
.sidebar-brand-sub { font-size: 10px; color: #374151; margin-top: 3px; text-transform: uppercase; letter-spacing: 0.12em; }
.section-label { font-size: 9px; color: #374151; text-transform: uppercase; letter-spacing: 0.14em; margin-bottom: 8px; }
.stButton > button { background: transparent !important; border: 1px solid #161622 !important; border-radius: 6px !important; color: #4b5563 !important; font-size: 12px !important; font-weight: 500 !important; padding: 8px 14px !important; width: 100% !important; text-align: left !important; margin-bottom: 2px !important; }
.stButton > button:hover { background: #161622 !important; color: #e2e8f0 !important; }
.filter-label { font-size: 9px; color: #374151; text-transform: uppercase; letter-spacing: 0.14em; margin: 18px 0 5px; }
.kpi { background: #0c0c14; border: 1px solid #161622; border-radius: 12px; padding: 20px 22px; position: relative; overflow: hidden; }
.kpi::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1.5px; background: linear-gradient(90deg, #f97316, #fb923c, #fdba74, transparent); }
.kpi-label { font-size: 9px; color: #374151; text-transform: uppercase; letter-spacing: 0.14em; margin-bottom: 10px; }
.kpi-value { font-size: 26px; font-weight: 700; color: #f1f5f9; letter-spacing: -0.03em; line-height: 1; }
.kpi-sub { font-size: 10px; color: #f97316; margin-top: 6px; }
.page-title { font-size: 18px; font-weight: 700; color: #f1f5f9; letter-spacing: -0.02em; display: inline; }
.page-sub { font-size: 11px; color: #374151; margin-top: 4px; margin-bottom: 20px; }
.live-dot { display: inline-block; width: 6px; height: 6px; background: #f97316; border-radius: 50%; margin-left: 8px; vertical-align: middle; box-shadow: 0 0 6px #f97316; }
.chart-card { background: #0c0c14; border: 1px solid #161622; border-radius: 12px; padding: 18px 20px 14px; margin-bottom: 14px; }
.chart-title { font-size: 10px; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.12em; margin-bottom: 14px; padding-bottom: 10px; border-bottom: 1px solid #161622; }
.chat-user { background: #161622; border: 1px solid #1e1e30; border-radius: 10px 10px 3px 10px; padding: 12px 16px; margin: 8px 0; color: #e2e8f0; font-size: 13px; line-height: 1.6; }
.chat-ai { background: #0c0c14; border: 1px solid #161622; border-left: 2px solid #f97316; border-radius: 3px 10px 10px 10px; padding: 12px 16px; margin: 8px 0; color: #cbd5e1; font-size: 13px; line-height: 1.6; }
.chat-label { font-size: 9px; text-transform: uppercase; letter-spacing: 0.12em; margin-bottom: 5px; }
.stDownloadButton > button { background: linear-gradient(135deg, #f97316, #fb923c) !important; color: white !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; }
.stTextInput input { background: #0c0c14 !important; border: 1px solid #161622 !important; border-radius: 8px !important; color: #f1f5f9 !important; font-size: 13px !important; }
.stSelectbox > div > div { background: #0c0c14 !important; border: 1px solid #161622 !important; color: #f1f5f9 !important; border-radius: 8px !important; }
.stMultiSelect > div > div { background: #0c0c14 !important; border: 1px solid #161622 !important; border-radius: 8px !important; }
.stMultiSelect span[data-baseweb="tag"] { background: #f9731620 !important; color: #fb923c !important; }
</style>
""", unsafe_allow_html=True)

GROQ_KEY = os.environ.get("GROQ_API_KEY", "")

@st.cache_data
def load_data():
    try:
        df = pd.read_csv("books_dataset.csv")
        rating_map = {"One":1,"Two":2,"Three":3,"Four":4,"Five":5}
        df["rating"] = df["rating"].map(rating_map)
        df["price"] = df["price"].astype(float)
        df.drop_duplicates(inplace=True)
        return df
    except FileNotFoundError:
        st.error("books_dataset.csv not found")
        st.stop()

df = load_data()

THEME = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#0c0c14", font=dict(family="Inter",color="#374151",size=11), xaxis=dict(gridcolor="#161622",linecolor="#161622",tickfont=dict(color="#4b5563"),zeroline=False), yaxis=dict(gridcolor="#161622",linecolor="#161622",tickfont=dict(color="#4b5563"),zeroline=False), margin=dict(l=0,r=0,t=4,b=0))
ORANGE = ["#0c0c14","#431407","#9a3412","#f97316","#fdba74"]

def ask_groq(question, context):
    system_prompt = (
        "أنت محلل بيانات سوق محترف. "
        "بياناتك: " + context + " "
        "رد دائماً بالعربي الفصيح. "
        "نظم ردك هكذا تماماً:\n"
        "## الإجابة\n"
        "جملة واحدة مباشرة.\n\n"
        "## التفاصيل\n"
        "- نقطة 1 مع أرقام من البيانات\n"
        "- نقطة 2 مع أرقام من البيانات\n"
        "- نقطة 3 مع أرقام من البيانات\n\n"
        "## الخلاصة\n"
        "جملة ختامية واحدة. الحد الأقصى 200 كلمة."
    )
    headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }
    try:
        r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=15)
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {e}"
