"""
FamousGate Hotels - Executive Monitoring Dashboard (Demo Version)
Run locally with: streamlit run app.py

✅ Supports REAL AI (OpenAI) when you add your API key in .streamlit/secrets.toml
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import hashlib
import random
import os
from openai import OpenAI

# ====================== PAGE CONFIG & THEME ======================
st.set_page_config(
    page_title="FamousGate Hotels | Executive Command Center",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for luxury dark theme
st.markdown("""
<style>
    .stApp {
        background-color: #0f172a;
        color: #e2e8f0;
    }
    .stMetric {
        background-color: #1e2937;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 16px;
    }
    .stMetric label {
        color: #94a3b8 !important;
    }
    .stMetric value {
        color: #f1f5f9 !important;
        font-size: 1.8rem !important;
    }
    .gold-text {
        color: #fbbf24;
        font-weight: 600;
    }
    .section-header {
        color: #fbbf24;
        border-bottom: 2px solid #fbbf24;
        padding-bottom: 8px;
        margin-bottom: 16px;
    }
    .stChatMessage {
        background-color: #1e2937;
        border-radius: 12px;
    }
    .stButton button {
        background-color: #fbbf24;
        color: #0f172a;
        font-weight: 600;
        border-radius: 8px;
    }
    .stButton button:hover {
        background-color: #f59e0b;
    }
</style>
""", unsafe_allow_html=True)

# ====================== FAKE DATA GENERATION ======================
BRANCHES = [
    {"name": "Bomet Town", "county": "Bomet", "rooms": 12, "lat": -0.7806, "lon": 35.3419},
    {"name": "Kyogong", "county": "Bomet", "rooms": 8, "lat": -0.8123, "lon": 35.4123},
    {"name": "Mogogoshiek", "county": "Bomet", "rooms": 10, "lat": -0.7541, "lon": 35.2890},
    {"name": "Sotik", "county": "Bomet", "rooms": 9, "lat": -0.6821, "lon": 35.1123},
    {"name": "Kaplong", "county": "Bomet", "rooms": 7, "lat": -0.7312, "lon": 35.3789},
    {"name": "Grill (Kericho)", "county": "Kericho", "rooms": 11, "lat": -0.3689, "lon": 35.2845},
    {"name": "Guesthouse (Kericho)", "county": "Kericho", "rooms": 6, "lat": -0.3621, "lon": 35.2912},
    {"name": "Kapsoit", "county": "Kericho", "rooms": 8, "lat": -0.3412, "lon": 35.2678},
    {"name": "Kaptote", "county": "Kericho", "rooms": 7, "lat": -0.3891, "lon": 35.3123},
    {"name": "Litein", "county": "Kericho", "rooms": 9, "lat": -0.4123, "lon": 35.2456},
]

def generate_fake_data(days=30):
    np.random.seed(42)
    end_date = datetime.now().date()
    dates = [end_date - timedelta(days=i) for i in range(days)][::-1]
    
    data = []
    for branch in BRANCHES:
        base_occupancy = np.random.randint(55, 92)
        for i, date in enumerate(dates):
            occ = max(35, min(98, base_occupancy + np.random.randint(-12, 15) + (i % 7 - 3) * 2))
            revenue = int(occ * branch["rooms"] * np.random.uniform(2800, 3600))
            checkins = int(occ * branch["rooms"] * 0.35)
            satisfaction = round(np.random.uniform(4.2, 4.95), 1)
            events = np.random.randint(0, 4)
            
            data.append({
                "date": date,
                "branch": branch["name"],
                "county": branch["county"],
                "rooms_total": branch["rooms"],
                "occupancy_pct": occ,
                "revenue_kes": revenue,
                "checkins": checkins,
                "satisfaction": satisfaction,
                "events_booked": events,
                "lat": branch["lat"],
                "lon": branch["lon"]
            })
    
    df = pd.DataFrame(data)
    current = df[df["date"] == end_date].copy()
    current["rooms_available"] = current["rooms_total"] - (current["occupancy_pct"] * current["rooms_total"] / 100).astype(int)
    
    return df, current, dates

df, current_df, date_range = generate_fake_data()

# ====================== AUTHENTICATION ======================
DIRECTORS = {
    "director@famousegatehotels.com": {"password": "Director2026!", "name": "James Kipchoge", "role": "Managing Director"},
    "finance@famousegatehotels.com": {"password": "Finance2026!", "name": "Grace Chepngetich", "role": "Finance Director"},
    "ops@famousegatehotels.com": {"password": "Ops2026!", "name": "Peter Rono", "role": "Operations Director"},
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

def login():
    st.markdown("## 🏨 FamousGate Hotels")
    st.markdown("### Executive Command Center — Demo")
    st.caption("Secure access for Directors only | Demo Mode with realistic fake data")
    
    with st.form("login_form"):
        email = st.text_input("Director Email", value="director@famousegatehotels.com")
        password = st.text_input("Password", type="password", value="Director2026!")
        submitted = st.form_submit_button("🔐 Sign In", use_container_width=True)
        
        if submitted:
            if email in DIRECTORS and password == DIRECTORS[email]["password"]:
                st.session_state.logged_in = True
                st.session_state.user = DIRECTORS[email]
                st.rerun()
            else:
                st.error("Invalid credentials. Please try again.")
                st.info("Demo credentials: director@famousegatehotels.com / Director2026!")

if not st.session_state.logged_in:
    login()
    st.stop()

# ====================== SIDEBAR ======================
user = st.session_state.user
st.sidebar.markdown(f"""
## 🏨 FamousGate Hotels
**Welcome, {user['name']}**  
*{user['role']}*
""")

st.sidebar.divider()

page = st.sidebar.radio(
    "Navigation",
    ["📊 Overview", "🗺️ Live Map & Occupancy", "💰 Revenue Analytics", 
     "🏢 Branch Performance", "📅 Bookings & Alerts", "🤖 AI Insights Chat"],
    index=0
)

st.sidebar.divider()

# Global filters
st.sidebar.markdown("### Filters")
selected_county = st.sidebar.multiselect(
    "Counties", ["Bomet", "Kericho"], default=["Bomet", "Kericho"]
)
date_from, date_to = st.sidebar.date_input(
    "Date Range",
    value=(date_range[0], date_range[-1]),
    min_value=date_range[0],
    max_value=date_range[-1]
)

filtered_df = df[
    (df["county"].isin(selected_county)) &
    (df["date"] >= date_from) &
    (df["date"] <= date_to)
]

st.sidebar.caption("🔄 Data refreshes every 60 seconds in production")
if st.sidebar.button("🔄 Refresh Data Now", use_container_width=True):
    st.rerun()

st.sidebar.divider()
st.sidebar.caption("**DEMO MODE** — All data is simulated\nProduction connects to live PMS & POS systems")

# ====================== OPENAI INTEGRATION ======================
def get_openai_client():
    """Get OpenAI client from secrets or environment variable"""
    api_key = None
    
    if hasattr(st, "secrets") and "OPENAI_API_KEY" in st.secrets:
        api_key = st.secrets["OPENAI_API_KEY"]
    elif os.getenv("OPENAI_API_KEY"):
        api_key = os.getenv("OPENAI_API_KEY")
    
    if api_key and api_key != "sk-your-openai-api-key-here":
        return OpenAI(api_key=api_key)
    return None

# ====================== AI CHATBOT ======================
def get_real_ai_response(question, df, current):
    client = get_openai_client()
    if not client:
        return None
    
    context = f"""
You are an executive assistant for FamousGate Hotels, a luxury hotel chain in Kenya with 10 branches.

Current data summary:
- Average occupancy: {df['occupancy_pct'].mean():.1f}%
- Today's total revenue: KES {current['revenue_kes'].sum():,.0f}
- Average guest satisfaction: {df['satisfaction'].mean():.2f}/5

Latest branch performance:
{current[['branch', 'occupancy_pct', 'revenue_kes', 'satisfaction']].to_string(index=False)}

Answer the user's question concisely and professionally.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": question}
            ],
            temperature=0.3,
            max_tokens=400
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ AI Error: {str(e)}"

def generate_ai_response(question, df, current):
    real_response = get_real_ai_response(question, df, current)
    if real_response:
        return real_response
    
    # Fallback mock responses
    q = question.lower().strip()
    
    if "occupancy" in q:
        avg = df["occupancy_pct"].mean()
        best = current.loc[current["occupancy_pct"].idxmax(), "branch"]
        worst = current.loc[current["occupancy_pct"].idxmin(), "branch"]
        return f"📊 Current average occupancy is **{avg:.1f}%**. Best: **{best}**, Lowest: **{worst}**."
    
    elif "revenue" in q and "today" in q:
        return f"💰 Today's total revenue: **KES {current['revenue_kes'].sum():,.0f}**."
    
    elif "compare" in q and "bomet" in q and "kericho" in q:
        bomet = df[df["county"]=="Bomet"]["revenue_kes"].sum()
        kericho = df[df["county"]=="Kericho"]["revenue_kes"].sum()
        return f"📈 Bomet: KES {bomet:,.0f} vs Kericho: KES {kericho:,.0f}."
    
    elif "best" in q or "top" in q:
        top = current.nlargest(3, "revenue_kes")["branch"].tolist()
        return f"🏆 Top branches: **{', '.join(top)}**"
    
    elif "satisfaction" in q:
        return f"⭐ Average satisfaction: **{df['satisfaction'].mean():.2f}/5**."
    
    else:
        return "I can answer questions about occupancy, revenue, satisfaction, and branch performance. Try: 'What is the occupancy in Litein?'"

# ====================== MAIN CONTENT ======================
col1, col2 = st.columns([4, 1])
with col1:
    st.markdown(f"# Executive Command Center")
    st.caption(f"Real-time view across all 10 branches • Last updated: {datetime.now().strftime('%d %b %Y, %H:%M')} EAT")
with col2:
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

st.divider()

# ====================== PAGES ======================
if page == "📊 Overview":
    st.markdown('<h2 class="section-header">📊 Executive Overview</h2>', unsafe_allow_html=True)
    
    total_occupancy = filtered_df["occupancy_pct"].mean()
    today_revenue = filtered_df[filtered_df["date"] == date_range[-1]]["revenue_kes"].sum()
    avg_satisfaction = filtered_df["satisfaction"].mean()
    total_checkins = filtered_df["checkins"].sum()
    
    kpi_cols = st.columns(4)
    kpi_cols[0].metric("Total Occupancy", f"{total_occupancy:.1f}%", "+4.2%")
    kpi_cols[1].metric("Today's Revenue", f"KES {today_revenue:,.0f}", "+12%")
    kpi_cols[2].metric("Avg Guest Rating", f"{avg_satisfaction:.1f}/5", "+0.1")
    kpi_cols[3].metric("Check-ins (Period)", f"{total_checkins:,}", "+87")
    
    st.markdown("---")
    
    col_left, col_right = st.columns([1.1, 1])
    with col_left:
        st.subheader("Occupancy Trend (Last 14 Days)")
        trend_df = filtered_df[filtered_df["date"] >= (date_range[-1] - timedelta(days=13))]
        fig = px.line(trend_df.groupby("date")["occupancy_pct"].mean().reset_index(), x="date", y="occupancy_pct", markers=True)
        fig.update_layout(height=320)
        st.plotly_chart(fig, use_container_width=True)
    
    with col_right:
        st.subheader("Revenue by County")
        rev = filtered_df.groupby("county")["revenue_kes"].sum().reset_index()
        fig = px.pie(rev, values="revenue_kes", names="county", color_discrete_sequence=["#fbbf24", "#34d399"])
        fig.update_layout(height=320)
        st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("🏆 Top Performing Branches")
    top = filtered_df.groupby("branch")["revenue_kes"].sum().nlargest(5).reset_index()
    st.dataframe(top, use_container_width=True, hide_index=True)

elif page == "🗺️ Live Map & Occupancy":
    st.markdown('<h2 class="section-header">🗺️ Live Occupancy Map</h2>', unsafe_allow_html=True)
    map_df = current_df.copy()
    map_df["size"] = map_df["occupancy_pct"] / 8
    fig = px.scatter_mapbox(map_df, lat="lat", lon="lon", size="size", color="occupancy_pct",
                            color_continuous_scale=["#ef4444", "#fbbf24", "#22c55e"], size_max=18,
                            zoom=7.8, center={"lat": -0.55, "lon": 35.28}, hover_name="branch")
    fig.update_layout(mapbox_style="carto-positron", height=520)
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Current Snapshot")
    st.dataframe(current_df[["branch", "county", "occupancy_pct", "revenue_kes", "satisfaction"]].sort_values("occupancy_pct", ascending=False), use_container_width=True)

elif page == "💰 Revenue Analytics":
    st.markdown('<h2 class="section-header">💰 Revenue Analytics</h2>', unsafe_allow_html=True)
    rev_trend = filtered_df.groupby("date")["revenue_kes"].sum().reset_index()
    fig = px.area(rev_trend, x="date", y="revenue_kes", color_discrete_sequence=["#fbbf24"])
    fig.update_layout(height=380)
    st.plotly_chart(fig, use_container_width=True)

elif page == "🏢 Branch Performance":
    st.markdown('<h2 class="section-header">🏢 Branch Performance</h2>', unsafe_allow_html=True)
    perf = filtered_df.groupby("branch").agg({"occupancy_pct": "mean", "revenue_kes": "sum", "satisfaction": "mean"}).reset_index().round(1)
    st.dataframe(perf.sort_values("revenue_kes", ascending=False), use_container_width=True)

elif page == "📅 Bookings & Alerts":
    st.markdown('<h2 class="section-header">📅 Bookings & Alerts</h2>', unsafe_allow_html=True)
    st.metric("Total Check-ins Today", int(current_df["checkins"].sum()))
    st.metric("Events Today", int(current_df["events_booked"].sum()))
    st.warning("⚠️ Litein occupancy dropped 18% this week")
    st.warning("🔥 Bomet Town at 94% occupancy — consider dynamic pricing")

elif page == "🤖 AI Insights Chat":
    st.markdown('<h2 class="section-header">🤖 AI Insights Chat</h2>', unsafe_allow_html=True)
    
    client = get_openai_client()
    if client:
        st.success("✅ Real AI Active (OpenAI GPT-4o-mini)")
    else:
        st.warning("⚠️ Demo Mode — Add your OpenAI key in `.streamlit/secrets.toml` to enable real AI")
    
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Hello! Ask me anything about the hotels."}]
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    if prompt := st.chat_input("Ask about occupancy, revenue, branches..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        response = generate_ai_response(prompt, filtered_df, current_df)
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

# ====================== FOOTER ======================
st.divider()
st.caption("© 2026 FamousGate Hotels Ltd. | Demo with realistic fake data | Ready for production")