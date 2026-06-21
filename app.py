import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from google import genai
from google.genai import types
import json
import hashlib
import os
from datetime import datetime, date, timedelta
import calendar
import random
from pathlib import Path
import base64

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Flowt · Smart Expense Tracker",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Inject Custom CSS ─────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg: #0d0f17;
    --surface: #161923;
    --surface2: #1e2334;
    --accent: #7c6dfa;
    --accent2: #f97316;
    --accent3: #10b981;
    --accent4: #f43f5e;
    --text: #e2e8f0;
    --muted: #64748b;
    --border: rgba(124,109,250,0.18);
}

html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

.stApp { background: var(--bg); }

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border);
}

/* Cards */
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 16px;
    transition: transform 0.2s, box-shadow 0.2s;
}
.card:hover { transform: translateY(-2px); box-shadow: 0 8px 32px rgba(124,109,250,0.12); }

.stat-card {
    background: linear-gradient(135deg, var(--surface) 0%, var(--surface2) 100%);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 20px;
    text-align: center;
}
.stat-number { font-size: 2rem; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
.stat-label { font-size: 0.8rem; color: var(--muted); text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }

/* Headings */
h1, h2, h3 { font-family: 'Space Grotesk', sans-serif !important; }

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, var(--accent) 0%, #9f8fff 100%);
    color: white !important;
    border: none;
    border-radius: 10px;
    font-weight: 600;
    padding: 10px 24px;
    transition: all 0.2s;
}
.stButton > button:hover { transform: translateY(-1px); box-shadow: 0 4px 20px rgba(124,109,250,0.4); }

/* Inputs */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div,
.stTextArea > div > div > textarea {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: 'Space Grotesk', sans-serif !important;
}

/* Metric overrides */
[data-testid="metric-container"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 16px !important;
}

/* Progress bar */
.stProgress > div > div > div {
    background: linear-gradient(90deg, var(--accent), var(--accent3));
}

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    background: var(--surface) !important;
    border-radius: 12px;
    padding: 4px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 8px !important;
    color: var(--muted) !important;
    font-weight: 500;
}
.stTabs [aria-selected="true"] {
    background: var(--accent) !important;
    color: white !important;
}

/* Hero banner */
.hero {
    background: linear-gradient(135deg, #1a1040 0%, #0d1a2e 50%, #0d0f17 100%);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 32px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -50px; right: -50px;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(124,109,250,0.25) 0%, transparent 70%);
}

/* Mood buttons */
.mood-btn {
    display: inline-flex; align-items: center; gap: 8px;
    background: var(--surface2); border: 1px solid var(--border);
    border-radius: 12px; padding: 10px 16px; cursor: pointer;
    transition: all 0.2s; font-size: 1.1rem;
}

/* Badge */
.badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.5px;
}
.badge-green { background: rgba(16,185,129,0.15); color: #10b981; border: 1px solid rgba(16,185,129,0.3); }
.badge-red   { background: rgba(244,63,94,0.15);  color: #f43f5e; border: 1px solid rgba(244,63,94,0.3); }
.badge-blue  { background: rgba(124,109,250,0.15); color: #9f8fff; border: 1px solid rgba(124,109,250,0.3); }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--accent); border-radius: 3px; }

/* Login card */
.login-container {
    max-width: 420px; margin: 60px auto;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 24px;
    padding: 48px 40px;
    text-align: center;
}

/* Appreciation banner */
.appreciation {
    background: linear-gradient(135deg, rgba(16,185,129,0.1) 0%, rgba(124,109,250,0.1) 100%);
    border: 1px solid rgba(16,185,129,0.3);
    border-radius: 12px;
    padding: 16px 20px;
    margin: 12px 0;
}

/* Dataframe */
[data-testid="stDataFrame"] { background: var(--surface) !important; border-radius: 12px; }

div[data-baseweb="select"] > div { background: var(--surface2) !important; border-color: var(--border) !important; }
</style>
""", unsafe_allow_html=True)


# ─── Data Layer ────────────────────────────────────────────────────────────────
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
USERS_FILE   = DATA_DIR / "users.json"
EXPENSE_FILE = DATA_DIR / "expenses.json"
GOALS_FILE   = DATA_DIR / "goals.json"

def load_json(path, default):
    if path.exists():
        with open(path) as f:
            try: return json.load(f)
            except: return default
    return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)

def hash_pw(pw): return hashlib.sha256(pw.encode()).hexdigest()

def register_user(email, pw, name):
    users = load_json(USERS_FILE, {})
    if email in users: return False, "Email already registered."
    users[email] = {"name": name, "pw": hash_pw(pw), "budget": 20000, "created": str(date.today())}
    save_json(USERS_FILE, users)
    return True, "Registered!"

def login_user(email, pw):
    users = load_json(USERS_FILE, {})
    if email not in users: return False, "Email not found."
    if users[email]["pw"] != hash_pw(pw): return False, "Wrong password."
    return True, users[email]

def get_expenses(email):
    all_exp = load_json(EXPENSE_FILE, {})
    return all_exp.get(email, [])

def save_expense(email, entry):
    all_exp = load_json(EXPENSE_FILE, {})
    if email not in all_exp: all_exp[email] = []
    entry["id"] = len(all_exp[email]) + 1
    all_exp[email].append(entry)
    save_json(EXPENSE_FILE, all_exp)

def delete_expense(email, exp_id):
    all_exp = load_json(EXPENSE_FILE, {})
    if email in all_exp:
        all_exp[email] = [e for e in all_exp[email] if e.get("id") != exp_id]
        save_json(EXPENSE_FILE, all_exp)

def get_goals(email):
    goals = load_json(GOALS_FILE, {})
    return goals.get(email, [])

def save_goal(email, goal):
    goals = load_json(GOALS_FILE, {})
    if email not in goals: goals[email] = []
    goals[email].append(goal)
    save_json(GOALS_FILE, goals)

def update_budget(email, budget):
    users = load_json(USERS_FILE, {})
    if email in users:
        users[email]["budget"] = budget
        save_json(USERS_FILE, users)

def get_user_info(email):
    users = load_json(USERS_FILE, {})
    return users.get(email, {})


# ─── Gemini AI ─────────────────────────────────────────────────────────────────
def init_gemini(api_key):
    client = genai.Client(api_key=api_key)
    return client

def gemini_generate(client, prompt):
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    return response.text

def ai_coach(client, expenses_df, budget, goal_text=""):
    if expenses_df.empty:
        prompt = f"I have a monthly budget of ₹{budget}. I haven't added expenses yet. Give me 3 short, actionable money tips as a friendly AI spending coach. Be concise and encouraging."
    else:
        total = expenses_df["amount"].sum()
        by_cat = expenses_df.groupby("category")["amount"].sum().to_dict()
        prompt = f"""You are a friendly AI spending coach. Monthly budget: ₹{budget}. Total spent so far: ₹{total:.0f}. 
Breakdown by category: {by_cat}. 
{'Goal: ' + goal_text if goal_text else ''}
Give 3 concise, personalized insights and 2 actionable tips. Use emojis. Keep it under 150 words."""
    try:
        return gemini_generate(client, prompt)
    except Exception as e:
        return f"AI coach unavailable: {str(e)}"

def mood_to_tag(client, mood_emoji, amount, category, description):
    prompt = f"""A user logged an expense of ₹{amount} in {category} ({description}) while feeling {mood_emoji}.
In one sentence (max 15 words), give a thoughtful observation linking their mood to this spending. Be warm, not judgmental."""
    try:
        return gemini_generate(client, prompt).strip()
    except:
        return ""

def detect_subscriptions(client, expenses_df):
    if expenses_df.empty: return "No expenses to analyse yet."
    recurring = expenses_df[expenses_df["category"].str.lower().isin(["subscription","entertainment","streaming","software","apps"])]
    if recurring.empty:
        sample = expenses_df.head(20).to_dict("records")
    else:
        sample = recurring.head(20).to_dict("records")
    prompt = f"""Analyse these transactions and identify likely recurring subscriptions or monthly charges. 
Transactions: {json.dumps(sample, default=str)}
List potential subscriptions with estimated monthly cost. Flag any that seem unused based on frequency. Be concise."""
    try:
        return gemini_generate(client, prompt)
    except Exception as e:
        return f"Subscription radar unavailable: {e}"


# ─── Charts ────────────────────────────────────────────────────────────────────
CHART_COLORS = ["#7c6dfa","#f97316","#10b981","#f43f5e","#0ea5e9","#a855f7","#eab308","#ec4899","#14b8a6","#6366f1"]

def make_donut(df, title):
    by_cat = df.groupby("category")["amount"].sum().reset_index()
    fig = px.pie(by_cat, names="category", values="amount", hole=0.55,
                 color_discrete_sequence=CHART_COLORS, title=title)
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Space Grotesk", color="#e2e8f0"),
        title_font_size=16, legend_font_size=12,
        margin=dict(t=40, b=10, l=10, r=10)
    )
    fig.update_traces(textfont_color="#e2e8f0")
    return fig

def make_bar_monthly(df):
    df["month_label"] = pd.to_datetime(df["date"]).dt.strftime("%b %Y")
    monthly = df.groupby("month_label")["amount"].sum().reset_index()
    monthly = monthly.sort_values("amount", ascending=False)
    fig = px.bar(monthly, x="month_label", y="amount",
                 color="amount", color_continuous_scale=["#1e2334","#7c6dfa","#f97316"],
                 title="Monthly Spending Overview")
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Space Grotesk", color="#e2e8f0"),
        coloraxis_showscale=False, title_font_size=16,
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
    )
    return fig

def make_line_trend(df):
    df2 = df.copy()
    df2["date"] = pd.to_datetime(df2["date"])
    daily = df2.groupby("date")["amount"].sum().reset_index()
    daily["cumulative"] = daily["amount"].cumsum()
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=daily["date"], y=daily["amount"],
        name="Daily Spend", line=dict(color="#7c6dfa", width=2),
        fill="tozeroy", fillcolor="rgba(124,109,250,0.1)"), secondary_y=False)
    fig.add_trace(go.Scatter(x=daily["date"], y=daily["cumulative"],
        name="Cumulative", line=dict(color="#f97316", width=2, dash="dot")), secondary_y=True)
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Space Grotesk", color="#e2e8f0"),
        title="Spending Trend", title_font_size=16,
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        legend=dict(bgcolor="rgba(0,0,0,0)")
    )
    return fig

def make_category_comparison(df, cat1, cat2):
    df2 = df.copy()
    df2["month"] = pd.to_datetime(df2["date"]).dt.strftime("%b %Y")
    d1 = df2[df2["category"]==cat1].groupby("month")["amount"].sum().reset_index().rename(columns={"amount":cat1})
    d2 = df2[df2["category"]==cat2].groupby("month")["amount"].sum().reset_index().rename(columns={"amount":cat2})
    merged = pd.merge(d1, d2, on="month", how="outer").fillna(0)
    fig = go.Figure()
    fig.add_trace(go.Bar(name=cat1, x=merged["month"], y=merged[cat1], marker_color="#7c6dfa"))
    fig.add_trace(go.Bar(name=cat2, x=merged["month"], y=merged[cat2], marker_color="#f97316"))
    fig.update_layout(
        barmode="group", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Space Grotesk", color="#e2e8f0"),
        title=f"{cat1} vs {cat2} Over Time", title_font_size=16,
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        legend=dict(bgcolor="rgba(0,0,0,0)")
    )
    return fig

def make_heatmap(df):
    df2 = df.copy()
    df2["date"] = pd.to_datetime(df2["date"])
    df2["dow"] = df2["date"].dt.day_name()
    df2["week"] = df2["date"].dt.isocalendar().week.astype(str)
    pivot = df2.pivot_table(index="dow", columns="week", values="amount", aggfunc="sum").fillna(0)
    days_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    pivot = pivot.reindex([d for d in days_order if d in pivot.index])
    fig = px.imshow(pivot, color_continuous_scale=["#0d0f17","#1e2334","#7c6dfa","#f97316"],
                    title="Spending Heatmap (by day of week)")
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Space Grotesk", color="#e2e8f0"), title_font_size=16,
    )
    return fig

def make_month_comparison_bar(prev_month, prev_amt, curr_month, curr_amt):
    diff = curr_amt - prev_amt
    pct  = (diff / prev_amt * 100) if prev_amt else 0
    fig = go.Figure(go.Bar(
        x=[prev_month, curr_month],
        y=[prev_amt, curr_amt],
        marker_color=["#7c6dfa", "#f43f5e" if diff > 0 else "#10b981"],
        text=[f"₹{prev_amt:,.0f}", f"₹{curr_amt:,.0f}"],
        textposition="outside",
        textfont=dict(color="#e2e8f0", family="JetBrains Mono")
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Space Grotesk", color="#e2e8f0"),
        title=f"Month Comparison · {'▲' if diff>0 else '▼'} ₹{abs(diff):,.0f} ({pct:+.1f}%)",
        title_font_size=16,
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        showlegend=False
    )
    return fig


# ─── MOODS ─────────────────────────────────────────────────────────────────────
MOODS = {"😊 Happy":"😊","😔 Sad":"😔","😤 Stressed":"😤","😌 Calm":"😌",
         "🥳 Excited":"🥳","😴 Tired":"😴","🤑 Splurgy":"🤑","😰 Anxious":"😰"}

CATEGORIES = ["Food & Dining","Transport","Shopping","Entertainment","Health & Medical",
               "Housing & Utilities","Education","Travel","Personal Care","Subscription",
               "Gifts & Donations","Investment","Other"]

APPRECIATION = [
    "🌟 Great job tracking your expenses! Financial awareness is the first step to freedom.",
    "💪 You're doing amazing — every rupee tracked is a rupee controlled!",
    "🎯 Consistency is key. Keep logging and watch your savings grow.",
    "🧠 Smart spenders track first, spend second. You're on the right path!",
    "✨ Your future self will thank you for this habit!",
]


# ─── LOGIN PAGE ────────────────────────────────────────────────────────────────
def login_page():
    col1, col2, col3 = st.columns([1,1.4,1])
    with col2:
        st.markdown("""
        <div style='text-align:center; padding: 40px 0 20px;'>
            <div style='font-size:3.5rem;'>💸</div>
            <h1 style='font-size:2.2rem; font-weight:700; margin:8px 0 4px; background:linear-gradient(90deg,#7c6dfa,#f97316); -webkit-background-clip:text; -webkit-text-fill-color:transparent;'>Flowt</h1>
            <p style='color:#64748b; font-size:0.95rem; margin-bottom:32px;'>Your AI-powered spending companion</p>
        </div>
        """, unsafe_allow_html=True)

        tab_login, tab_reg = st.tabs(["🔑 Sign In", "✨ Register"])

        with tab_login:
            st.markdown("<br>", unsafe_allow_html=True)
            email = st.text_input("Email", placeholder="you@example.com", key="li_email")
            pw    = st.text_input("Password", type="password", placeholder="••••••••", key="li_pw")
            if st.button("Sign In →", use_container_width=True):
                ok, result = login_user(email, pw)
                if ok:
                    st.session_state.logged_in = True
                    st.session_state.email = email
                    st.session_state.user = result
                    st.rerun()
                else:
                    st.error(result)

        with tab_reg:
            st.markdown("<br>", unsafe_allow_html=True)
            name  = st.text_input("Full Name", placeholder="Suparna Das", key="r_name")
            email = st.text_input("Email", placeholder="you@example.com", key="r_email")
            pw    = st.text_input("Password", type="password", placeholder="Min 6 chars", key="r_pw")
            pw2   = st.text_input("Confirm Password", type="password", placeholder="••••••••", key="r_pw2")
            if st.button("Create Account →", use_container_width=True):
                if not name or not email or not pw:
                    st.error("Please fill all fields.")
                elif pw != pw2:
                    st.error("Passwords don't match.")
                elif len(pw) < 6:
                    st.error("Password too short.")
                else:
                    ok, msg = register_user(email, pw, name)
                    if ok: st.success("Account created! Sign in now.")
                    else:  st.error(msg)


# ─── MAIN APP ──────────────────────────────────────────────────────────────────
def main_app():
    email    = st.session_state.email
    user     = get_user_info(email)
    expenses = get_expenses(email)
    df       = pd.DataFrame(expenses) if expenses else pd.DataFrame(columns=["id","date","amount","category","description","mood","mood_note","payment_method"])
    if not df.empty:
        df["date"]   = pd.to_datetime(df["date"])
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)

    budget = user.get("budget", 20000)
    name   = user.get("name", "User")

    # ─── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(f"""
        <div style='padding:16px 0 8px; text-align:center;'>
            <div style='font-size:2rem;'>💸</div>
            <div style='font-size:1.2rem; font-weight:700; color:#7c6dfa;'>Flowt</div>
            <div style='font-size:0.8rem; color:#64748b; margin-top:4px;'>Hey, {name.split()[0]}! 👋</div>
        </div>
        <hr style='border-color:rgba(124,109,250,0.15); margin:12px 0;'>
        """, unsafe_allow_html=True)

        page = st.radio("", ["🏠 Dashboard","➕ Add Expense","📊 Analytics","🔍 Transactions",
                              "🎯 Goals","🤖 AI Coach","📡 Sub Radar","⚙️ Settings"],
                        label_visibility="collapsed")

        st.markdown("<hr style='border-color:rgba(124,109,250,0.15);'>", unsafe_allow_html=True)

        # Budget ring
        total_spent = df["amount"].sum() if not df.empty else 0
        pct = min(total_spent / budget, 1.0) if budget else 0
        bar_color = "#10b981" if pct < 0.7 else "#f97316" if pct < 0.9 else "#f43f5e"
        st.markdown(f"""
        <div style='font-size:0.75rem; color:#64748b; text-transform:uppercase; letter-spacing:1px; margin-bottom:6px;'>Budget Used</div>
        <div style='font-size:1.5rem; font-weight:700; font-family:JetBrains Mono,monospace; color:{bar_color};'>₹{total_spent:,.0f}</div>
        <div style='font-size:0.8rem; color:#64748b;'>of ₹{budget:,}</div>
        """, unsafe_allow_html=True)
        st.progress(pct)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚪 Sign Out", use_container_width=True):
            for k in ["logged_in","email","user"]: st.session_state.pop(k, None)
            st.rerun()

    # ── PAGE: DASHBOARD ────────────────────────────────────────────────────────
    if page == "🏠 Dashboard":
        st.markdown(f"""
        <div class='hero'>
            <div style='font-size:0.8rem; color:#7c6dfa; letter-spacing:2px; text-transform:uppercase; margin-bottom:8px;'>Welcome back</div>
            <h1 style='font-size:2rem; font-weight:700; margin:0 0 8px;'>{name} ✦</h1>
            <p style='color:#64748b; margin:0; font-size:0.95rem;'>{random.choice(APPRECIATION)}</p>
        </div>
        """, unsafe_allow_html=True)

        # KPI row
        savings = max(budget - total_spent, 0)
        this_month_df = df[df["date"].dt.month == datetime.now().month] if not df.empty else df
        this_month_total = this_month_df["amount"].sum() if not this_month_df.empty else 0

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("💰 Total Spent", f"₹{total_spent:,.0f}")
        with c2:
            st.metric("📅 This Month", f"₹{this_month_total:,.0f}")
        with c3:
            st.metric("🎯 Budget Left", f"₹{max(budget-this_month_total,0):,.0f}")
        with c4:
            st.metric("💎 Total Savings", f"₹{savings:,.0f}")

        st.markdown("<br>", unsafe_allow_html=True)

        if not df.empty and len(df) >= 2:
            col1, col2 = st.columns(2)
            with col1: st.plotly_chart(make_donut(df, "Spending by Category"), use_container_width=True)
            with col2: st.plotly_chart(make_line_trend(df), use_container_width=True)

            # Recent 5
            st.markdown("### 🕐 Recent Transactions")
            recent = df.sort_values("date", ascending=False).head(5)
            for _, r in recent.iterrows():
                mood_icon = r.get("mood","") or ""
                st.markdown(f"""
                <div class='card' style='padding:14px 20px; display:flex; justify-content:space-between; align-items:center;'>
                    <div>
                        <span style='font-weight:600;'>{r.get('description','—')}</span>
                        <span class='badge badge-blue' style='margin-left:8px;'>{r.get('category','')}</span>
                        {f"<span style='margin-left:6px;'>{mood_icon}</span>" if mood_icon else ""}
                    </div>
                    <div style='text-align:right;'>
                        <div style='font-size:1.1rem; font-weight:700; font-family:JetBrains Mono,monospace; color:#f97316;'>₹{r['amount']:,.0f}</div>
                        <div style='font-size:0.75rem; color:#64748b;'>{str(r['date'])[:10]}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("🎉 No expenses yet! Head to **Add Expense** to get started.")

    # ── PAGE: ADD EXPENSE ──────────────────────────────────────────────────────
    elif page == "➕ Add Expense":
        st.markdown("## ➕ Log an Expense")

        # Gemini API check
        api_key = st.session_state.get("gemini_key","")

        col1, col2 = st.columns([1.5, 1])
        with col1:
            st.markdown("### 😊 How are you feeling?")
            mood_cols = st.columns(4)
            selected_mood = st.session_state.get("selected_mood","")
            for i, (label, emoji) in enumerate(MOODS.items()):
                with mood_cols[i % 4]:
                    if st.button(label, key=f"mood_{i}", use_container_width=True):
                        st.session_state.selected_mood = emoji
                        selected_mood = emoji

            if selected_mood:
                st.markdown(f"<div class='appreciation'>Current mood: <b>{selected_mood}</b> — Your mood may influence spending patterns!</div>", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### 📝 Expense Details")

            col_a, col_b = st.columns(2)
            with col_a:
                exp_date  = st.date_input("Date", value=date.today())
                amount    = st.number_input("Amount (₹)", min_value=0.0, step=50.0, format="%.2f")
            with col_b:
                category  = st.selectbox("Category", CATEGORIES)
                payment   = st.selectbox("Payment Method", ["UPI","Cash","Credit Card","Debit Card","Net Banking","Wallet"])

            description = st.text_input("Description", placeholder="e.g. Swiggy dinner, Ola ride...")

            # Voice input note
            st.markdown("""
            <div style='background:rgba(124,109,250,0.08); border:1px solid rgba(124,109,250,0.2); border-radius:10px; padding:12px 16px; margin:8px 0;'>
                🎤 <b>Voice Input</b> — Use browser's voice input on the Description field (right-click mic icon or use Google's voice keyboard on mobile)
            </div>
            """, unsafe_allow_html=True)

            if st.button("💾 Save Expense", use_container_width=True):
                if amount <= 0:
                    st.error("Enter a valid amount.")
                elif not description:
                    st.error("Please add a description.")
                else:
                    mood_note = ""
                    if selected_mood and api_key:
                        try:
                            client = init_gemini(api_key)
                            mood_note = mood_to_tag(client, selected_mood, amount, category, description)
                        except: pass

                    entry = {
                        "date": str(exp_date),
                        "amount": amount,
                        "category": category,
                        "description": description,
                        "mood": selected_mood,
                        "mood_note": mood_note,
                        "payment_method": payment,
                    }
                    save_expense(email, entry)
                    st.session_state.selected_mood = ""
                    st.success(f"✅ ₹{amount:,.0f} saved!")
                    if mood_note:
                        st.markdown(f"<div class='appreciation'>🤖 {mood_note}</div>", unsafe_allow_html=True)
                    st.balloons()

        with col2:
            st.markdown("### 📊 Quick Stats")
            if not df.empty:
                today_df  = df[df["date"].dt.date == date.today()]
                week_ago  = date.today() - timedelta(days=7)
                week_df   = df[df["date"].dt.date >= week_ago]
                st.metric("Today's Spend", f"₹{today_df['amount'].sum():,.0f}")
                st.metric("This Week",     f"₹{week_df['amount'].sum():,.0f}")
                st.metric("Total Entries", f"{len(df)}")
                if not df.empty:
                    top_cat = df.groupby("category")["amount"].sum().idxmax()
                    st.metric("Top Category", top_cat)

    # ── PAGE: ANALYTICS ────────────────────────────────────────────────────────
    elif page == "📊 Analytics":
        st.markdown("## 📊 Analytics")

        if df.empty:
            st.info("Add some expenses to see analytics!")
            return

        tab1, tab2, tab3, tab4, tab5 = st.tabs(["Overview","Category","Time Trends","Month Compare","Heatmap"])

        with tab1:
            c1, c2 = st.columns(2)
            with c1: st.plotly_chart(make_donut(df, "All-time Category Breakdown"), use_container_width=True)
            with c2: st.plotly_chart(make_bar_monthly(df), use_container_width=True)

        with tab2:
            categories = df["category"].unique().tolist()
            if len(categories) >= 2:
                col1, col2 = st.columns(2)
                with col1: cat1 = st.selectbox("Category 1", categories, index=0)
                with col2: cat2 = st.selectbox("Category 2", [c for c in categories if c != cat1], index=0)
                if cat1 and cat2:
                    st.plotly_chart(make_category_comparison(df, cat1, cat2), use_container_width=True)
            else:
                st.info("Add expenses in at least 2 categories for comparison.")

        with tab3:
            st.plotly_chart(make_line_trend(df), use_container_width=True)

        with tab4:
            st.markdown("#### Monthly Expenses Comparison")
            months = df["date"].dt.to_period("M").unique()
            months_str = [str(m) for m in sorted(months)]
            if len(months_str) >= 2:
                col1, col2 = st.columns(2)
                with col1: m1 = st.selectbox("Month 1", months_str, index=0)
                with col2: m2 = st.selectbox("Month 2", months_str, index=len(months_str)-1)
                amt1 = df[df["date"].dt.to_period("M").astype(str)==m1]["amount"].sum()
                amt2 = df[df["date"].dt.to_period("M").astype(str)==m2]["amount"].sum()
                st.plotly_chart(make_month_comparison_bar(m1, amt1, m2, amt2), use_container_width=True)
                diff = amt2 - amt1
                st.markdown(f"""
                <div class='card'>
                    <div style='display:grid; grid-template-columns:1fr 1fr 1fr; gap:16px; text-align:center;'>
                        <div><div class='stat-label'>{m1} Expenses</div><div class='stat-number' style='color:#7c6dfa;'>₹{amt1:,.0f}</div></div>
                        <div><div class='stat-label'>{m2} Expenses</div><div class='stat-number' style='color:#f97316;'>₹{amt2:,.0f}</div></div>
                        <div><div class='stat-label'>{"Increase" if diff>0 else "Decrease"}</div>
                             <div class='stat-number' style='color:{"#f43f5e" if diff>0 else "#10b981"};'>₹{abs(diff):,.0f}</div></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("Need at least 2 months of data for comparison.")
                # Demo
                st.plotly_chart(make_month_comparison_bar("April 2025", 10000, "May 2025", 12000), use_container_width=True)
                st.markdown("""
                <div class='card'>
                    <div style='display:grid; grid-template-columns:1fr 1fr 1fr; gap:16px; text-align:center;'>
                        <div><div class='stat-label'>April Expenses</div><div class='stat-number' style='color:#7c6dfa;'>₹10,000</div></div>
                        <div><div class='stat-label'>May Expenses</div><div class='stat-number' style='color:#f97316;'>₹12,000</div></div>
                        <div><div class='stat-label'>Increase</div><div class='stat-number' style='color:#f43f5e;'>₹2,000</div></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with tab5:
            if len(df) >= 7:
                st.plotly_chart(make_heatmap(df), use_container_width=True)
            else:
                st.info("Add at least 7 expenses to see the spending heatmap.")

    # ── PAGE: TRANSACTIONS ─────────────────────────────────────────────────────
    elif page == "🔍 Transactions":
        st.markdown("## 🔍 All Transactions")

        if df.empty:
            st.info("No transactions yet."); return

        # Filters
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            date_from = st.date_input("From", value=df["date"].min().date())
        with col2:
            date_to   = st.date_input("To",   value=df["date"].max().date())
        with col3:
            cats = ["All"] + sorted(df["category"].unique().tolist())
            cat_filter = st.selectbox("Category", cats)
        with col4:
            sort_by = st.selectbox("Sort by", ["Most Recent","Oldest","Highest Amount","Lowest Amount"])

        filtered = df[(df["date"].dt.date >= date_from) & (df["date"].dt.date <= date_to)]
        if cat_filter != "All":
            filtered = filtered[filtered["category"] == cat_filter]

        if sort_by == "Most Recent":    filtered = filtered.sort_values("date", ascending=False)
        elif sort_by == "Oldest":       filtered = filtered.sort_values("date", ascending=True)
        elif sort_by == "Highest Amount": filtered = filtered.sort_values("amount", ascending=False)
        elif sort_by == "Lowest Amount":  filtered = filtered.sort_values("amount", ascending=True)

        st.markdown(f"**{len(filtered)} transactions** · Total: **₹{filtered['amount'].sum():,.0f}**")

        # Display
        for _, r in filtered.iterrows():
            mood_icon = r.get("mood","") or ""
            mood_note = r.get("mood_note","") or ""
            c1, c2, c3 = st.columns([3,1,0.5])
            with c1:
                st.markdown(f"""
                <div class='card' style='padding:14px 18px;'>
                    <div style='display:flex; justify-content:space-between; align-items:flex-start;'>
                        <div>
                            <span style='font-weight:600;'>{r.get('description','—')}</span>
                            <span class='badge badge-blue' style='margin-left:8px;'>{r.get('category','')}</span>
                            {f"<span style='margin-left:4px;'>{mood_icon}</span>" if mood_icon else ""}
                            <div style='font-size:0.78rem; color:#64748b; margin-top:4px;'>{str(r['date'])[:10]} · {r.get('payment_method','')}</div>
                            {f"<div style='font-size:0.8rem; color:#7c6dfa; margin-top:4px; font-style:italic;'>💬 {mood_note}</div>" if mood_note else ""}
                        </div>
                        <div style='text-align:right; min-width:80px;'>
                            <div style='font-size:1.1rem; font-weight:700; font-family:JetBrains Mono,monospace; color:#f97316;'>₹{r['amount']:,.0f}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with c3:
                if st.button("🗑️", key=f"del_{r.get('id',r.name)}"):
                    delete_expense(email, r.get("id"))
                    st.rerun()

    # ── PAGE: GOALS ────────────────────────────────────────────────────────────
    elif page == "🎯 Goals":
        st.markdown("## 🎯 Goals & Savings")

        goals = get_goals(email)
        this_month_total = df[df["date"].dt.month == datetime.now().month]["amount"].sum() if not df.empty else 0
        savings = max(budget - this_month_total, 0)

        # Current month summary
        st.markdown(f"""
        <div class='card'>
            <div style='display:grid; grid-template-columns:1fr 1fr 1fr; gap:20px; text-align:center;'>
                <div>
                    <div class='stat-label'>Monthly Budget</div>
                    <div class='stat-number' style='color:#7c6dfa;'>₹{budget:,}</div>
                </div>
                <div>
                    <div class='stat-label'>Expenses This Month</div>
                    <div class='stat-number' style='color:#f43f5e;'>₹{this_month_total:,.0f}</div>
                </div>
                <div>
                    <div class='stat-label'>Savings Added for Goal</div>
                    <div class='stat-number' style='color:#10b981;'>₹{savings:,.0f}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Budget progress
        pct = min(this_month_total / budget, 1.0) if budget else 0
        bar_color = "#10b981" if pct < 0.7 else "#f97316" if pct < 0.9 else "#f43f5e"
        st.markdown(f"<div style='font-size:0.85rem; color:#64748b; margin:16px 0 6px;'>Budget Utilization: <b style='color:{bar_color};'>{pct*100:.1f}%</b></div>", unsafe_allow_html=True)
        st.progress(pct)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### ➕ Add New Goal")
        col1, col2, col3 = st.columns(3)
        with col1: goal_text   = st.text_input("Your Goal", placeholder="Buy a laptop, Trip to Goa...")
        with col2: goal_amount = st.number_input("Target Amount (₹)", min_value=0.0, step=1000.0)
        with col3: goal_by     = st.date_input("Target Date", value=date.today() + timedelta(days=90))

        if st.button("🎯 Set Goal"):
            if not goal_text or goal_amount <= 0:
                st.error("Fill goal details.")
            else:
                save_goal(email, {"goal": goal_text, "amount": goal_amount, "by": str(goal_by),
                                  "created": str(date.today()), "saved": savings})
                st.success("Goal set! 🎉"); st.rerun()

        if goals:
            st.markdown("### 📋 Your Goals")
            for g in reversed(goals):
                total_saved = g.get("saved", 0)
                target = g.get("amount", 1)
                progress = min(total_saved / target, 1.0) if target else 0
                st.markdown(f"""
                <div class='card'>
                    <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;'>
                        <div>
                            <span style='font-weight:600; font-size:1.05rem;'>🎯 {g['goal']}</span>
                            <span class='badge badge-blue' style='margin-left:10px;'>By {g['by']}</span>
                        </div>
                        <div style='font-family:JetBrains Mono,monospace; font-size:1.1rem; color:#10b981;'>
                            ₹{total_saved:,.0f} / ₹{target:,.0f}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.progress(progress)

    # ── PAGE: AI COACH ─────────────────────────────────────────────────────────
    elif page == "🤖 AI Coach":
        st.markdown("## 🤖 AI Spending Coach")
        api_key = st.session_state.get("gemini_key","")

        if not api_key:
            st.warning("⚙️ Please add your Gemini API key in **Settings** first.")
            return

        goals    = get_goals(email)
        goal_txt = goals[-1]["goal"] if goals else ""

        st.markdown("""
        <div class='hero' style='padding:24px;'>
            <div style='font-size:0.8rem; color:#7c6dfa; letter-spacing:2px; text-transform:uppercase;'>Powered by Gemini</div>
            <h3 style='margin:6px 0;'>Your Personal Finance Coach 🧠</h3>
            <p style='color:#64748b; margin:0; font-size:0.9rem;'>AI-generated insights based on your real spending data</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🔄 Get Fresh Insights", use_container_width=True):
            with st.spinner("Analysing your spending..."):
                client  = init_gemini(api_key)
                insight = ai_coach(client, df, budget, goal_txt)
                st.session_state.ai_insight = insight

        if "ai_insight" in st.session_state:
            st.markdown(f"""
            <div class='card' style='border-color:rgba(124,109,250,0.4);'>
                <div style='font-size:0.8rem; color:#7c6dfa; text-transform:uppercase; letter-spacing:1px; margin-bottom:10px;'>🤖 AI Coach Says</div>
                <div style='line-height:1.7; color:#e2e8f0;'>{st.session_state.ai_insight.replace(chr(10),'<br>')}</div>
            </div>
            """, unsafe_allow_html=True)

        # Custom question
        st.markdown("### 💬 Ask Your Coach")
        question = st.text_area("Ask anything about your finances...", placeholder="e.g. How can I save ₹5000 this month? Am I spending too much on food?")
        if st.button("Ask →"):
            if question:
                with st.spinner("Thinking..."):
                    client = init_gemini(api_key)
                    context = f"User's monthly budget: ₹{budget}. Total spent: ₹{total_spent:.0f}."
                    if not df.empty:
                        context += f" Category breakdown: {df.groupby('category')['amount'].sum().to_dict()}"
                    prompt = f"{context}\n\nUser question: {question}\n\nAnswer concisely as a friendly financial advisor. Use emojis sparingly."
                    try:
                        client = init_gemini(api_key)
                        answer = gemini_generate(client, prompt)
                        st.markdown(f"""
                        <div class='appreciation'>
                            <b>Coach:</b> {answer.replace(chr(10),'<br>')}
                        </div>
                        """, unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Error: {e}")

    # ── PAGE: SUBSCRIPTION RADAR ───────────────────────────────────────────────
    elif page == "📡 Sub Radar":
        st.markdown("## 📡 Subscription Radar")
        api_key = st.session_state.get("gemini_key","")

        st.markdown("""
        <div style='background:rgba(249,115,22,0.08); border:1px solid rgba(249,115,22,0.3); border-radius:12px; padding:16px 20px; margin-bottom:20px;'>
            🔍 <b>Subscription Radar</b> scans your transactions to detect recurring charges and potential forgotten subscriptions.
        </div>
        """, unsafe_allow_html=True)

        if not api_key:
            st.warning("Add your Gemini API key in Settings.")
            return

        if st.button("🔍 Scan for Subscriptions", use_container_width=True):
            with st.spinner("Scanning transactions..."):
                client  = init_gemini(api_key)
                result = detect_subscriptions(client, df)
                st.session_state.sub_radar = result

        if "sub_radar" in st.session_state:
            st.markdown(f"""
            <div class='card' style='border-color:rgba(249,115,22,0.4);'>
                <div style='font-size:0.8rem; color:#f97316; text-transform:uppercase; letter-spacing:1px; margin-bottom:10px;'>📡 Radar Results</div>
                <div style='line-height:1.8; color:#e2e8f0;'>{st.session_state.sub_radar.replace(chr(10),'<br>')}</div>
            </div>
            """, unsafe_allow_html=True)

        # Manual sub tracker
        st.markdown("### ➕ Track a Subscription Manually")
        col1, col2, col3 = st.columns(3)
        with col1: sub_name  = st.text_input("Service Name", placeholder="Netflix, Spotify...")
        with col2: sub_amt   = st.number_input("Monthly Cost (₹)", min_value=0.0, step=10.0)
        with col3: sub_cycle = st.selectbox("Billing Cycle", ["Monthly","Quarterly","Yearly"])
        if st.button("Add Subscription"):
            if sub_name and sub_amt > 0:
                entry = {"date": str(date.today()), "amount": sub_amt, "category": "Subscription",
                         "description": f"[Sub] {sub_name} ({sub_cycle})", "mood": "", "mood_note": "", "payment_method":"Auto-debit"}
                save_expense(email, entry)
                st.success(f"✅ {sub_name} added!"); st.rerun()

    # ── PAGE: SETTINGS ─────────────────────────────────────────────────────────
    elif page == "⚙️ Settings":
        st.markdown("## ⚙️ Settings")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 🔑 Gemini API Key")
            api_key = st.text_input("Paste your Gemini API key",
                                    type="password",
                                    value=st.session_state.get("gemini_key",""),
                                    placeholder="AIza...")
            if st.button("Save API Key"):
                st.session_state.gemini_key = api_key
                st.success("✅ Key saved for this session!")

            st.markdown("""
            <div style='font-size:0.8rem; color:#64748b; margin-top:8px;'>
                Get your free key at <a href='https://aistudio.google.com/app/apikey' target='_blank' style='color:#7c6dfa;'>aistudio.google.com</a>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("### 💰 Monthly Budget")
            new_budget = st.number_input("Set Budget (₹)", value=int(budget), min_value=1000, step=500)
            if st.button("Update Budget"):
                update_budget(email, new_budget)
                st.success(f"✅ Budget updated to ₹{new_budget:,}"); st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 🎨 Chart Style")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div class='appreciation'>
                ✅ Dark theme enabled — optimized for late-night budgeting sessions 🌙
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("🗑️ Danger Zone"):
            st.warning("This will permanently delete all your expense data.")
            if st.button("Delete All My Expenses", type="primary"):
                all_exp = load_json(EXPENSE_FILE, {})
                all_exp[email] = []
                save_json(EXPENSE_FILE, all_exp)
                st.success("All expenses deleted."); st.rerun()


# ─── ROUTER ────────────────────────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login_page()
else:
    main_app()
