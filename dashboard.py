import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import matplotlib.pyplot as plt
from datetime import datetime
import time
import altair as alt
import plotly.graph_objects as go


current_date = datetime.today().strftime("%d %b %Y")


# Define scope and credentials
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
print("Authorization successfull...")
# Paste your Google Sheet URL here
sheet_url = "https://docs.google.com/spreadsheets/d/1vy1gQ8tkYpCcNIOuSpguSk5-oHT0MTGBcDmIufTISX8/edit?gid=0#gid=0"
sheet = client.open_by_url(sheet_url).sheet1
print("sheet accessed...")

PPAZI_LHMC_DailyReport_sheet_url = "https://docs.google.com/spreadsheets/d/1o6VaiDxr9WpPoNZHkpXK1GRljATVxArPbdUXUyZ3-Bw/edit?gid=1049115440#gid=1049115440"
PreScr_sheet = client.open_by_url(PPAZI_LHMC_DailyReport_sheet_url).worksheet("PreScr")


# Read data
@st.cache_data(ttl=300)
def load_prescreen_data_with_retry(retries=3, delay=5):
    for attempt in range(retries):
        try:
            data = PreScr_sheet.get_all_records()
            print(f"data reading attempt number: {attempt}")
            return pd.DataFrame(data)
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                raise e

try:
    df = load_prescreen_data_with_retry()
    # st.success("✅ Data loaded successfully")         # this shows on the main dashboard that it is a success.
    print(" Data loaded successfully")
except Exception as e:
    st.error(f"⚠️ Could not load data: {e}")
    print(f"could not load data: {e}")


# -------------------------------------------------------------Dashboard layout----------------------------------------------------

# Sample values
total_prescreened = 4150
eligible = 1623
screened = 1596
pending = 24
non_eligible = 2530
ineligibility_reasons = {
    "GA Ineligibility": 2051,
    "Distance": 761,
    "Pregnancy not live": 19,
    "Age": 15
}
exclusion_count = 534
exclusion_criteria = {
    "Planning to go out of the current residence within next 6 months": 212,
    "Planning to deliver in other hospital": 181,
    "Heart Disease": 0,
    "Jaundice": 16,
    "Severe illness": 68,
    "Severe Allergy": 6,
    "Consuming antibiotics": 75,
    "Taking treatment for RTI": 31,
    "Cervical incompetency": 8,
    "Enrollment target acheived for today": 70
}
# --- Left side values ---
refusal_or_reschedule = 184
total_crp_done = 574
total_enrolled = 528

# --- Right side bar chart values ---
risk_factors = {
    "Only 1 high risk factor": 292,
    "2 high risk factors": 213,
    "3 high risk factors": 93,
    ">=4 high risk factors": 26
}
# --- First Column Data: Not Enrolled Reasons ---
not_enrolled_reasons = {
    "Not enrolled (Enrolled Reason)": 355,
    "No inclusion criteria met": 250,
    "Consent Refusal": 94,
    "Eligible by LMP but excluded by USG": 1
}
not_enrolled_df = pd.DataFrame(list(not_enrolled_reasons.items()), columns=["Reason", "Count"])

# --- Second Column Data: Enrollment Reasons ---
enrollment_reasons = {
    "Past H/O of fetal loss": 280,
    "Delivered before 37 weeks": 40,
    "Baby birth weight < 2500g": 70,
    "H/O diabetes": 41,
    "Recurrent H/O RTI": 7,
    "RTI in last 6 months": 12,
    "H/O RTI Partner": 3,
    "HB <10.5": 248,
    "CRP ≥10": 60,
    "MUAC <24": 196,
    "BMI <18.5 (Malnourished)": 70,
    "BMI ≥30 (Malnourished)": 83
}
screening_refused = 184
total_crp = 574
exclusion_count = 668  # Or sum(exclusion_criteria.values())
exclusion_criteria = {
    "Out of residence": 212,
    "Other hospital": 182,
    "Heart Disease": 0,
    "Jaundice": 16,
    "Severe illness": 68,
    "Allergy": 6,
    "Antibiotics": 75,
    "RTI Treatment": 31,
    "Cervical incompetency": 8,
    "Target Achieved": 70
}
not_enrolled_reasons = {
    "Not enrolled Enrolled Reason": 355,
    "No inclusion criteria met": 250,
    "Consent Refusal": 94,
    "Eligible by LMP then in screening form excluded by USG": 1
}


# Page config
st.set_page_config(page_title="Screening Dashboard", layout="wide")
# Title and Date
left_col, right_col = st.columns([4, 1])
with left_col:
    st.title("📊 PPAZI Study Dashboard")
with right_col:
    st.markdown(
        f"""
        <div style="text-align: right; font-size: 20px; font-weight: 600; margin-top: 20px;">
            📅 {current_date}
        </div>
        """,
        unsafe_allow_html=True
    )
st.divider()


# 🧪 Total Pre-Screened (centered)
st.markdown(f"""
<div style='text-align: center;'>
    <h3>🧪 Total Pre-Screened: {total_prescreened}</h3>
</div>
""", unsafe_allow_html=True)
st.markdown(f"""
<div style="display: flex; justify-content: space-between; width: 100%; margin-bottom: 1rem;">
    <div style="flex: 1; text-align: left; white-space: nowrap; font-size: 22px;">
        ✅ <strong>Eligible for Screening: {eligible}</strong>
    </div>
    <div style="flex: 1; text-align: right; white-space: nowrap; font-size: 22px;">
        ❌ <strong>Non-Eligible for Screening: {non_eligible}                    </strong>
    </div>
</div>
""", unsafe_allow_html=True)
# Layout: Left - Pie - Right
left_col, center_col, right_col = st.columns([2, 1.5, 2])
# ✅ Eligible for Screening
with left_col:
    col1, col2 = st.columns(2)
    col1.metric("📋 Screened", screened)
    col2.metric("⏳ Pending Screening", pending)
# 🥧 Pie Chart in Center (Plotly)
with center_col:
    labels = ["Screened", "Pending", "Non-Eligible"]
    values = [screened, pending, non_eligible]
    fig = go.Figure(data=[
        go.Pie(
            labels=labels,
            values=values,
            hole=0,  # Fully filled pie
            hoverinfo="label+percent+value",
            textinfo="label+percent",
            textfont_size=12,
            marker=dict(line=dict(color='#000000', width=1)),
            pull=[0.05, 0.05, 0.05]  # Slight 3D effect
        )
    ])
    fig.update_layout(
        height=250,
        width=350,
        margin=dict(t=10, b=10, l=10, r=10),
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)
# ❌ Non-Eligible Reasons (2x2 Grid)
with right_col:
    row1_col1, row1_col2 = st.columns(2)
    row1_col1.metric("GA Ineligibility", ineligibility_reasons["GA Ineligibility"])
    row1_col2.metric("Distance", ineligibility_reasons["Distance"])
    row2_col1, row2_col2 = st.columns(2)
    row2_col1.metric("Pregnancy not live", ineligibility_reasons["Pregnancy not live"])
    row2_col2.metric("Age", ineligibility_reasons["Age"])
    st.markdown(
    """
    <div style='text-align: center; font-size: 10px; font-style: italic; margin-top: 0px;'>
        *(Multiple reasons are present)
    </div>
    """,
    unsafe_allow_html=True)
st.divider()


# --- Layout: two columns ---
left_col, right_col = st.columns(2)
enrollment_df = pd.DataFrame(enrollment_reasons.items(), columns=["Reason", "Count"])
# --- Left Column ---
with left_col:
    st.subheader(f"Total Enrolled: {total_enrolled}")
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; width: 100%; margin-bottom: 1rem;">
        <div style="flex: 1; text-align: left; white-space: nowrap; font-size: 22px;">
            ✅ <strong> Reasons for Enrollment </strong>
        </div>
    </div>
    """, unsafe_allow_html=True)
    # st.subheader("✅ Reasons for Enrollment")
    st.dataframe(enrollment_df, use_container_width=True)
    st.markdown(
    """
    <div style='text-align: center; font-size: 10px; font-style: italic; margin-top: 0px;'>
        *(Multiple reasons are present)
    </div>
    """,
    unsafe_allow_html=True
)
# --- Right Column: Bar Chart ---
with right_col:
    df_risk = pd.DataFrame(list(risk_factors.items()), columns=["Risk Factor", "Count"])
    st.markdown(
        """
        <div style="margin-top: 60px;">
        """,
        unsafe_allow_html=True
    )
    base = alt.Chart(df_risk).encode(
        y=alt.Y("Risk Factor:N", sort='-x', title=""),
        x=alt.X("Count:Q", title="")
    )
    bars = base.mark_bar().encode(
        color=alt.Color("Risk Factor:N", legend=None)
    )
    text = base.mark_text(
        align='left',
        baseline='middle',
        dx=3  # padding between bar and text
    ).encode(text="Count:Q")
    chart = (bars + text).properties(height=250)
    st.altair_chart(chart, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    # Spacing between chart and metrics
    st.markdown("<br>", unsafe_allow_html=True)
    # Create 3 columns: left spacer, center content, right spacer
    spacer_left, center_col, spacer_right = st.columns([1, 2, 1])
    with center_col:
        # Centered vertical metrics
        st.metric("📝 Screening Refused / Scheduled ANC", screening_refused)
        st.metric("🧪 Total CRP Done", total_crp)
st.divider()



# DataFrames
exclusion_df = pd.DataFrame(exclusion_criteria.items(), columns=["Criteria", "Count"])
not_enrolled_df = pd.DataFrame(not_enrolled_reasons.items(), columns=["Reason", "Count"])

# Layout
left_col, right_col = st.columns(2)

# 🚫 LEFT COLUMN — Enrollment Exclusion
with left_col:
    st.subheader(f"🚫 Exclusion Criteria for Enrollment: {exclusion_count}")
    st.dataframe(exclusion_df, use_container_width=True)

    st.markdown(
        """
        <div style='text-align: center; font-size: 10px; font-style: italic; margin-top: 0px;'>
            *(Multiple reasons are present)
        </div>
        """,
        unsafe_allow_html=True
    )

# 🚫 RIGHT COLUMN — Reasons for Not Enrolled (Bar Chart with labels and values)
with right_col:
    st.subheader("🚫 Reasons for Not Enrolled")

    bar = (
        alt.Chart(not_enrolled_df)
        .mark_bar()
        .encode(
            x=alt.X("Count:Q", title=""),
            y=alt.Y("Reason:N", sort='-x', title=""),
            color=alt.Color("Reason:N", legend=None)
        )
        .properties(height=250)
    )

    # Text layer to show count values at end of bars
    text = (
        alt.Chart(not_enrolled_df)
        .mark_text(align="left", baseline="middle", dx=3)
        .encode(
            x="Count:Q",
            y=alt.Y("Reason:N", sort='-x'),
            text="Count:Q"
        )
    )

    # Combine bar and text
    combined_chart = (bar + text).configure_view(strokeWidth=0)
    st.altair_chart(combined_chart, use_container_width=True)

st.divider()
