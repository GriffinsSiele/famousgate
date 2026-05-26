"""
FamousGate Hotels - Executive Monitoring Dashboard (Demo Version)
Run locally with: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import hashlib
import random

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
    .branch-card {
        background-color: #1e2937;
        border-radius: 10px;
        padding: 12px;
        margin: 6px 0;
        border-left: 4px solid #fbbf24;
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
    
    # Current snapshot
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

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

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

# ====================== MAIN CONTENT ======================

# Header
col1, col2 = st.columns([4, 1])
with col1:
    st.markdown(f"# Executive Command Center")
    st.caption(f"Real-time view across all 10 branches • Last updated: {datetime.now().strftime('%d %b %Y, %H:%M')} EAT")
with col2:
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

st.divider()

# ====================== PAGE: OVERVIEW ======================
if page == "📊 Overview":
    st.markdown('<h2 class="section-header">📊 Executive Overview</h2>', unsafe_allow_html=True)
    
    # KPI Cards
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
    
    # Charts row
    col_left, col_right = st.columns([1.1, 1])
    
    with col_left:
        st.subheader("Occupancy Trend (Last 14 Days)")
        trend_df = filtered_df[filtered_df["date"] >= (date_range[-1] - timedelta(days=13))]
        fig_trend = px.line(
            trend_df.groupby("date")["occupancy_pct"].mean().reset_index(),
            x="date", y="occupancy_pct",
            markers=True, title="Average Daily Occupancy %"
        )
        fig_trend.update_layout(height=320, showlegend=False)
        st.plotly_chart(fig_trend, use_container_width=True)
    
    with col_right:
        st.subheader("Revenue by County")
        rev_county = filtered_df.groupby("county")["revenue_kes"].sum().reset_index()
        fig_pie = px.pie(rev_county, values="revenue_kes", names="county", 
                         color_discrete_sequence=["#fbbf24", "#34d399"])
        fig_pie.update_layout(height=320)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # Top performing branches
    st.subheader("🏆 Top Performing Branches (by Revenue)")
    top_branches = filtered_df.groupby("branch")["revenue_kes"].sum().nlargest(5).reset_index()
    st.dataframe(top_branches, use_container_width=True, hide_index=True)

# ====================== PAGE: LIVE MAP ======================
elif page == "🗺️ Live Map & Occupancy":
    st.markdown('<h2 class="section-header">🗺️ Live Occupancy Map — All Branches</h2>', unsafe_allow_html=True)
    
    # Current snapshot map
    map_df = current_df.copy()
    map_df["size"] = map_df["occupancy_pct"] / 8  # scale for visibility
    
    fig_map = px.scatter_mapbox(
        map_df,
        lat="lat", lon="lon",
        size="size",
        color="occupancy_pct",
        color_continuous_scale=["#ef4444", "#fbbf24", "#22c55e"],
        size_max=18,
        zoom=7.8,
        center={"lat": -0.55, "lon": 35.28},
        hover_name="branch",
        hover_data={"occupancy_pct": ":.1f", "revenue_kes": ":,.0f", "county": True},
        title="Current Occupancy by Branch (size = occupancy level)"
    )
    fig_map.update_layout(
        mapbox_style="carto-positron",
        height=520,
        margin={"r":0,"t":40,"l":0,"b":0}
    )
    st.plotly_chart(fig_map, use_container_width=True)
    
    # Current metrics table
    st.subheader("Current Snapshot — All Branches")
    display_cols = ["branch", "county", "occupancy_pct", "rooms_available", "revenue_kes", "satisfaction"]
    st.dataframe(
        current_df[display_cols].sort_values("occupancy_pct", ascending=False),
        use_container_width=True,
        column_config={
            "occupancy_pct": st.column_config.ProgressColumn("Occupancy %", format="%.1f%%", min_value=0, max_value=100),
            "revenue_kes": st.column_config.NumberColumn("Revenue (KES)", format="KES %d"),
            "satisfaction": st.column_config.NumberColumn("Rating", format="%.1f ⭐")
        }
    )

# ====================== PAGE: REVENUE ======================
elif page == "💰 Revenue Analytics":
    st.markdown('<h2 class="section-header">💰 Revenue Analytics</h2>', unsafe_allow_html=True)
    
    rev_trend = filtered_df.groupby("date")["revenue_kes"].sum().reset_index()
    fig_rev = px.area(rev_trend, x="date", y="revenue_kes", 
                       title="Total Daily Revenue Trend", color_discrete_sequence=["#fbbf24"])
    fig_rev.update_layout(height=380)
    st.plotly_chart(fig_rev, use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Revenue by Branch (Period)")
        branch_rev = filtered_df.groupby("branch")["revenue_kes"].sum().sort_values(ascending=True)
        fig_bar = px.bar(branch_rev, orientation='h', title="Total Revenue (KES)")
        fig_bar.update_layout(height=420)
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with col2:
        st.subheader("Average Daily Revenue per Branch")
        avg_rev = filtered_df.groupby("branch")["revenue_kes"].mean().sort_values(ascending=False).reset_index()
        st.dataframe(avg_rev, use_container_width=True, hide_index=True)

# ====================== PAGE: BRANCH PERFORMANCE ======================
elif page == "🏢 Branch Performance":
    st.markdown('<h2 class="section-header">🏢 Branch Performance Comparison</h2>', unsafe_allow_html=True)
    
    perf = filtered_df.groupby("branch").agg({
        "occupancy_pct": "mean",
        "revenue_kes": "sum",
        "satisfaction": "mean",
        "events_booked": "sum"
    }).reset_index().round(1)
    perf = perf.sort_values("revenue_kes", ascending=False)
    
    st.dataframe(
        perf,
        use_container_width=True,
        column_config={
            "occupancy_pct": st.column_config.ProgressColumn("Avg Occupancy", format="%.1f%%"),
            "revenue_kes": st.column_config.NumberColumn("Total Revenue", format="KES %d"),
            "satisfaction": st.column_config.NumberColumn("Avg Rating", format="%.1f")
        }
    )
    
    # Comparison chart
    fig_compare = px.bar(perf, x="branch", y=["occupancy_pct", "satisfaction"], 
                         barmode="group", title="Occupancy vs Satisfaction by Branch")
    st.plotly_chart(fig_compare, use_container_width=True)

# ====================== PAGE: BOOKINGS & ALERTS ======================
elif page == "📅 Bookings & Alerts":
    st.markdown('<h2 class="section-header">📅 Bookings, Events & Smart Alerts</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1.3])
    
    with col1:
        st.subheader("Today's Key Metrics")
        today_data = current_df
        st.metric("Total Check-ins Today", int(today_data["checkins"].sum()))
        st.metric("Events Scheduled Today", int(today_data["events_booked"].sum()))
        st.metric("Rooms Available Now", int(today_data["rooms_available"].sum()))
    
    with col2:
        st.subheader("🚨 Active Alerts (Demo)")
        alerts = [
            "⚠️ Litein occupancy dropped 18% week-over-week — investigate",
            "🔥 Bomet Town at 94% occupancy — consider dynamic pricing",
            "📉 Kapsoit satisfaction at 4.3 — review recent feedback",
            "🎉 Mogogoshiek exceeded monthly revenue target by 22%"
        ]
        for alert in alerts:
            st.warning(alert)
    
    st.subheader("Upcoming Events (Next 7 Days)")
    st.info("In production this would pull live from the events booking system. Demo shows sample events.")

# ====================== PAGE: AI CHATBOT ======================
elif page == "🤖 AI Insights Chat":
    st.markdown('<h2 class="section-header">🤖 AI Insights Chat — Ask Anything</h2>', unsafe_allow_html=True)
    st.caption("Powered by Grok (xAI) simulation • Ask questions about occupancy, revenue, branches, trends, etc.")
    
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I'm your AI Executive Assistant. I have full access to all branch data. How can I help you today?"}
        ]
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    if prompt := st.chat_input("Ask about any branch, metric, or trend..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Smart mock AI response
        response = generate_ai_response(prompt, filtered_df, current_df)
        
        with st.chat_message("assistant"):
            st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})

def generate_ai_response(question, df, current):
    q = question.lower().strip()
    
    if "occupancy" in q:
        avg = df["occupancy_pct"].mean()
        best = current.loc[current["occupancy_pct"].idxmax(), "branch"]
        worst = current.loc[current["occupancy_pct"].idxmin(), "branch"]
        return f"📊 Current average occupancy across all branches is **{avg:.1f}%**. Best performer: **{best}** ({current.loc[current['branch']==best, 'occupancy_pct'].values[0]:.1f}%). Lowest: **{worst}**."
    
    elif "revenue" in q and "today" in q:
        today_rev = current["revenue_kes"].sum()
        return f"💰 Today's total revenue across all branches is **KES {today_rev:,.0f}**."
    
    elif "compare" in q or "vs" in q:
        if "bomet" in q and "kericho" in q:
            bomet_rev = df[df["county"]=="Bomet"]["revenue_kes"].sum()
            kericho_rev = df[df["county"]=="Kericho"]["revenue_kes"].sum()
            return f"📈 Bomet County total revenue: **KES {bomet_rev:,.0f}** vs Kericho: **KES {kericho_rev:,.0f}**."
        return "I can compare any two branches or counties. Try: 'Compare Bomet Town vs Litein revenue'"
    
    elif "best" in q or "top" in q:
        top = current.nlargest(3, "revenue_kes")["branch"].tolist()
        return f"🏆 Top 3 branches by today's revenue: **{', '.join(top)}**"
    
    elif "alert" in q or "problem" in q:
        return "🚨 Current concerns: Litein occupancy is trending down. Kapsoit guest satisfaction needs attention. All other branches are performing above target."
    
    elif "satisfaction" in q:
        avg_sat = df["satisfaction"].mean()
        return f"⭐ Average guest satisfaction is **{avg_sat:.2f}/5**. Highest rated branch is currently **{current.loc[current['satisfaction'].idxmax(), 'branch']}**."
    
    else:
        return ("I can answer questions about occupancy, revenue, satisfaction, branch comparisons, trends, and alerts. "
                "Try examples like:\n"
                "• What is the occupancy in Litein today?\n"
                "• Compare revenue between Bomet and Kericho\n"
                "• Which branch has the highest satisfaction?")

# ====================== FOOTER ======================
st.divider()
st.caption("© 2026 FamousGate Hotels Ltd. | This is a fully functional **demo** with realistic fake data. "
           "In production this connects to live Property Management System, POS, and guest feedback platforms. "
           "Built with Streamlit • Ready for deployment.")

# Save a small note
st.sidebar.caption("💡 Tip: Try asking the AI chatbot complex questions!")