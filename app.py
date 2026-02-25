import streamlit as st
import pandas as pd
import plotly.express as px
from db import get_ai_impact_data,get_daily_portfolio_data,get_ai_suggestions,get_campaign_names,get_campaign_daily_data,get_campaign_performance_summary

# st.set_page_config(page_title="AI Ads Impact Dashboard", layout="wide")
st.set_page_config(layout="wide")
# st.markdown("""
# <style>
# .stApp { background-color: #f8f9fa; color: #212529; }
# .main-header { font-size: 2.2rem; color: #4a4a4a; font-weight: 700; margin-bottom: .25rem; }
# .metric-card {
#     background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#     padding: 1.0rem; border-radius: 12px; color: white; text-align: center; margin: .5rem 0;
#     box-shadow: 0 4px 6px rgba(0,0,0,.1);
# }
# .executive-summary {
#     background-color: white; border-radius: 12px; padding: 1.2rem; box-shadow: 0 4px 6px rgba(0,0,0,.05);
#     margin-bottom: 1.2rem; border-left: 4px solid #764ba2;
# }
# .assistant-message { 
#     background-color: #f8f9fa; 
#     border-radius: 12px; 
#     padding: 1rem; 
#     border-left: 4px solid #667eea;
#     margin-bottom: 1rem;
# }
# .insight-card {
#     background-color: #fff;
#     border-radius: 8px;
#     padding: 1rem;
#     margin: 0.5rem 0;
#     box-shadow: 0 2px 4px rgba(0,0,0,0.05);
#     border-left: 4px solid #ffd700;
# }
# .recommendation-card {
#     background-color: #f0f8ff;
#     border-radius: 8px;
#     padding: 1rem;
#     margin: 0.5rem 0;
#     box-shadow: 0 2px 4px rgba(0,0,0,0.05);
#     border-left: 4px solid #4682b4;
# }
# .conversation-item {
#     background-color: white;
#     border-radius: 8px;
#     padding: 1rem;
#     margin: 0.5rem 0;
#     box-shadow: 0 2px 4px rgba(0,0,0,0.05);
#     border-left: 4px solid #e0e0e0;
# }
# .stButton button {
#     use_container_width: 100%;
# }
# .css-1d391kg {padding: 1.5rem;}
# </style>
# """, unsafe_allow_html=True)

st.markdown("""
<style>

/* Main app background + text */
.stApp {
    background-color: #f8f9fa;
    color: #212529 !important;
}

/* ALL text elements */
html, body, [class*="css"]  {
    color: #212529 !important;
}

/* Headers */
h1, h2, h3, h4, h5, h6 {
    color: #1f2937 !important;
}

/* Radio labels */
.stRadio label {
    color: #212529 !important;
    font-weight: 600;
}

/* Selectbox labels */
.stSelectbox label {
    color: #212529 !important;
    font-weight: 600;
}

/* Metrics text */
[data-testid="stMetricValue"] {
    color: #111827 !important;
}
.kpi-card {
    background-color: #ffffff;
    padding: 24px;
    border-radius: 16px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.06);
    text-align: center;
    border: 1px solid #e5e7eb;
}

.kpi-title {
    font-size: 15px;
    color: #6b7280;
    font-weight: 600;
    letter-spacing: 0.5px;
}

.kpi-value {
    font-size: 36px;
    font-weight: 700;
    color: #6b7280;
    margin-top: 8px;
}
            
/* Radio group container */
div[role="radiogroup"] {
    display: flex;
    gap: 20px;
}

/* Each radio option */
div[role="radiogroup"] label {
    background-color: #e5e7eb;   /* light grey background */
    padding: 8px 18px;
    border-radius: 20px;
    color: #111827 !important;   /* dark text */
    font-weight: 600;
    cursor: pointer;
}

/* Selected option */
div[role="radiogroup"] input:checked + div {
    background-color: #d1d5db !important;  /* medium grey */
    color: #111827 !important;
}
            
/* Only fix radio text visibility */
div[role="radiogroup"] label {
    color: black !important;
}

# /* Radio label title */
# .stRadio > label {
#     font-size: 18px;
#     font-weight: 600;
#     color: #6b7280 !important;
# }

# /* Radio options text */
# div[role="radiogroup"] label {
#     color: #6b7280 !important;
#     font-weight: 600;
# }

# # /* Selected radio circle color */
# # div[role="radiogroup"] input:checked + div {
# #     background-color: #4f46e5 !important;
# # }

# /* Improve spacing */
# div[role="radiogroup"] {
#     gap: 30px;
# }
 

</style>
""", unsafe_allow_html=True)



st.title("🤖 AI Ads Optimization Impact Dashboard")

st.markdown("### View Mode")

view_mode = st.radio(
    "Select Mode",
    ["Impact Analysis", "Suggestion View"],
    horizontal=True
)


# load data
raw_df = get_ai_impact_data().dropna()
portfolio_df = get_daily_portfolio_data()

campaign_df = get_campaign_names()


# convert date safely
raw_df["action_date"] = pd.to_datetime(raw_df["action_date"], errors="coerce")
raw_df = raw_df.dropna(subset=["action_date"])

cycle_dates = sorted(raw_df["action_date"].unique())


# create week column
# create 7-day action window label
raw_df["week_range"] = (
    raw_df["action_date"].dt.strftime("%b %d")
    + " - " +
    (raw_df["action_date"] + pd.Timedelta(days=6)).dt.strftime("%b %d")
)

raw_df["week"] = raw_df["action_date"].dt.strftime("%Y - Week %U")

portfolio_df = portfolio_df.sort_values("report_date")

anchor_date = pd.to_datetime("2026-02-05")

portfolio_df["week_number"] = (
    (portfolio_df["report_date"] - anchor_date).dt.days // 7
)

anchor_date = pd.to_datetime("2026-02-05")

raw_df["week_number"] = (
    (pd.to_datetime(raw_df["action_date"]) - anchor_date).dt.days // 7
)

weekly = (
    portfolio_df
    .groupby("week_number")
    .agg({
        "report_date": ["min", "max"],
        "total_sales": "sum",
        "total_spend": "sum"
    })
    .reset_index()
)

weekly.columns = ["week_number", "start_date", "end_date", "total_sales", "total_spend"]

weekly["avg_roas"] = weekly["total_sales"] / weekly["total_spend"]

weekly["week_range"] = (
    weekly["start_date"].dt.strftime("%d %b")
    + " – " +
    weekly["end_date"].dt.strftime("%d %b")
)
weekly = weekly[weekly["start_date"] >= pd.to_datetime("2026-01-29")]


# fig = px.line(
#     weekly,
#     x="week_range",
#     y="avg_roas",
#     markers=True,
#     title="Weekly Portfolio ROAS Trend"
# )

# st.plotly_chart(fig, use_container_width=True)

weekly_roas = (
    portfolio_df
    .groupby("week_number")
    .agg({
        "total_sales": "sum",
        "total_spend": "sum"
    })
    .reset_index()
)

weekly_roas["portfolio_roas"] = (
    weekly_roas["total_sales"] /
    weekly_roas["total_spend"]
)

weekly_ai = (
    raw_df
    .groupby("week_number")["roas_change"]
    .mean()
    .reset_index()
)

merged = weekly_roas.merge(
    weekly[["week_number", "week_range"]],
    on="week_number",
    how="left"
)

# st.markdown("### Filters")

# col1, col2 = st.columns(2)

# # Campaign dropdown
# with col1:
#     campaigns = sorted(raw_df["campaign_id"].unique())
#     selected_campaign = st.selectbox("Campaign ID", campaigns)

# # Week dropdown
# with col2:
#     week_list = weekly.sort_values("week_number")["week_range"].tolist()
#     selected_week = st.selectbox("Week", week_list)


# df = raw_df[
#     (raw_df["campaign_id"] == selected_campaign) &
#     (raw_df["week_range"] == selected_week)
# ].copy()


# selected_week_row = weekly[weekly["week_range"] == selected_week]
# selected_week_number = selected_week_row["week_number"].iloc[0]

# df = raw_df[
#     (raw_df["campaign_id"] == selected_campaign) &
#     (raw_df["week_number"] == selected_week_number)
# ].copy()

# has_impact_data = df["roas_change"].notna().any()

if view_mode == "Impact Analysis" :
    st.markdown("### Filters")
    col1, col2 = st.columns(2)

    # Campaign dropdown
    with col1:
        # campaigns = sorted(campaigns.unique())
        # campaign_list = sorted(campaigns["Campaign ID"].tolist())
        campaign_list=['City Targeting (Kolkata) 28 aug ']
        # selected_campaign = st.selectbox("Campaign ID", campaign_list)
        # selected_campaign = int(selected_campaign)
        # campaign_list = sorted(campaign_df["campaign_name"].tolist())
        selected_campaign = st.selectbox("Campaign Name", campaign_list)

    # Week dropdown
    with col2:
        week_list = weekly.sort_values("week_number")["week_range"].tolist()
        selected_week = st.selectbox("Week", week_list)
        
    selected_week_row = weekly[weekly["week_range"] == selected_week]
    selected_week_number = selected_week_row["week_number"].iloc[0]

    selected_campaign_id = campaign_df[
        campaign_df["campaign_name"] == selected_campaign
    ]["campaign_id"].iloc[0]

    df = raw_df[
        (raw_df["campaign_id"] == selected_campaign_id) &
        (raw_df["week_number"] == selected_week_number)
    ].copy()
    campaign_daily_df = get_campaign_daily_data(selected_campaign_id)
    campaign_daily_df["week_number"] = (
        (campaign_daily_df["report_date"] - anchor_date).dt.days // 7
    )
    week_daily_df = campaign_daily_df[
        campaign_daily_df["week_number"] == selected_week_number
    ].copy()
    
    # has_impact_data = df["roas_change"].notna().any()

    # if not has_impact_data:
    #     st.warning("No impact data available for the selected campaign and week.")
    #     st.stop()
    

    def classify(row):
        if row["action"] == "PAUSE" and row["spend_after"] == 0:
            return "Saved Budget 💰"
        elif row["roas_change"] > 0:
            return "Success ✅"
        else:
            return "Failed ❌"

    df["result"] = df.apply(classify, axis=1)

    # Get portfolio weekly data for selected week
    weekly_selected = weekly[weekly["week_range"] == selected_week]

    # st.write("Selected Week:", selected_week)
    # st.write("Weekly Selected Row:")
    # st.write(weekly_selected)


    if not weekly_selected.empty:
        week_roas = weekly_selected["avg_roas"].iloc[0]
        week_spend = weekly_selected["total_spend"].iloc[0]
    else:
        week_roas = 0
        week_spend = 0


    st.markdown("### 📊 Weekly Performance Summary")

    col1, col2 = st.columns(2)

    # 1️⃣ AI Success Rate
    # if len(df) > 0:
    #     success_rate = (df["result"] == "Success ✅").mean() * 100
    # else:
    #     success_rate = 0

    # 2️⃣ Portfolio ROAS (Weekly)
    # already computed above

    # 3️⃣ Portfolio Spend (Weekly)

    # col1.metric("AI Success Rate", f"{success_rate:.1f}%")
    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Weekly ROAS</div>
            <div class="kpi-value">{week_roas:.2f}</div>
        </div>
    """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Weekly Spend</div>
            <div class="kpi-value">₹{week_spend:,.0f}</div>
        </div>
    """, unsafe_allow_html=True)
    # col1.metric("Weekly ROAS", f"{week_roas:.2f}")
    # col2.metric("Weekly Spend", f"₹{week_spend:,.0f}")

    st.header("📅 Daily Performance (Selected Week)")

    # fig = px.bar(
    #     week_daily_df,
    #     x="report_date",
    #     y="roas",
    #     title="Daily ROAS",
    # )
    fig = px.bar(
        week_daily_df,
        x="report_date",
        y="roas",
        title="Daily ROAS",
        text="roas"   # 👈 show values
    )

    # Format labels
    fig.update_traces(
        texttemplate="%{text:.2f}",   # 2 decimal places
        textposition="outside"        # show above bar
    )

    # Reduce chart height
    fig.update_layout(
        height=350,   # 👈 smaller height (try 300–400)
        yaxis_title="ROAS",
        xaxis_title="Date"
    )

    st.plotly_chart(fig, use_container_width=True)

    # st.markdown("### 📊 AI Performance Summary")

    # col1, col2, col3, col4 = st.columns(4)

    # success_rate = (df["result"] == "Success ✅").mean() * 100
    # avg_roas_lift = df["roas_change"].mean()
    # spend_saved = df[df["spend_change"] < 0]["spend_change"].sum()
    # impressions = df["impressions_after"].sum()

    # col1.metric("Success Rate", f"{success_rate:.1f}%")
    # col2.metric("Avg ROAS Change", f"{avg_roas_lift:.2f}")
    # col3.metric("Spend Saved", f"₹{abs(spend_saved):,.0f}")
    # col4.metric("Impressions After", f"{impressions:,.0f}")


    # st.markdown("### 📈 Impact Visualisation")
    # col1, col2 = st.columns(2)

    # with col1:
    #     fig = px.bar(
    #         raw_df,
    #         x="targeting",
    #         y=["roas_before", "roas_after"],
    #         barmode="group",
    #         title="ROAS Before vs After"
    #     )
    #     st.plotly_chart(fig, use_container_width=True)

    # with col2:
    #     pie = px.pie(raw_df, names="result", title="Decision Outcomes")
    #     st.plotly_chart(pie, use_container_width=True)


    # st.header("AI Decision Success Distribution")

    # pie = px.pie(raw_df, names="result", title="Decision Outcomes")
    # st.plotly_chart(pie, use_container_width=True)




    fig = px.line(
        weekly,
        x="week_range",
        y="avg_roas",
        markers=True,
        title="Weekly Portfolio ROAS Trend"
    )

    st.plotly_chart(fig, use_container_width=True)


    df = df.reset_index(drop=True)


    st.header("Keyword Decision Scorecard")


    st.data_editor(
        df[[
            "targeting",
            "action",
            "roas_before",
            "roas_after",
            "roas_change",
            "spend_before",
            "spend_after",
            "spend_change",
            "impressions_before",
            "impressions_after",
            "result",
            "explanation"
        ]],
        use_container_width=True,
        height=500,
        disabled=True
    )

    st.header("ROAS Before vs After")

    fig = px.bar(
        df,
        x="targeting",
        y=["roas_before", "roas_after"],
        barmode="group",
        title="Keyword ROAS Comparison"
    )
    st.plotly_chart(fig, use_container_width=True)

    # st.markdown("### 🧠 Keyword Decision Scoreboard")

    # df = df.sort_values("roas_change", ascending=False)

    # for _, row in df.iterrows():
    #     with st.container():
    #         col1, col2, col3, col4 = st.columns([2,1,1,1])
            
    #         col1.markdown(f"**{row['targeting']}**")
    #         col2.markdown(f"Action: **{row['action']}**")
    #         col3.markdown(f"ROAS: **{row['roas_before']:.2f} → {row['roas_after']:.2f}**")
    #         col4.markdown(f"Result: **{row['result']}**")

    #         # expandable explanation
    #         with st.expander("Why did AI suggest this?"):
    #             st.write(row["explanation"])

    #         st.markdown("---")



if view_mode == "Suggestion View":
    st.header("📌 Latest AI Suggestions")
    st.markdown("### Filters")

    col1, = st.columns(1)

    # Campaign dropdown
    with col1:
        # campaigns = sorted(campaigns.unique())
        campaign_list = ["All"] + sorted(campaign_df["campaign_name"].tolist())
        selected_campaign = st.selectbox("Campaign Name", campaign_list)
    
    suggestions_raw_df = get_ai_suggestions()

    # suggestions_df = suggestions_raw_df[
    #     suggestions_raw_df["campaign_id"] == selected_campaign
    # ].copy()
    if selected_campaign == "All":
        suggestions_df = suggestions_raw_df.copy()
    else:
        selected_id = campaign_df[
            campaign_df["campaign_name"] == selected_campaign
        ]["campaign_id"].iloc[0]

        suggestions_df = suggestions_raw_df[
            suggestions_raw_df["campaign_id"] == selected_id
        ].copy()
    suggestions_df = suggestions_df.merge(
        campaign_df[["campaign_id", "campaign_name"]],
        on="campaign_id",
        how="left"
    )

    suggestions_df = suggestions_df.sort_values("action_date", ascending=False)
    
    suggestions_df = suggestions_df.reset_index(drop=True)
    if suggestions_df.empty:
        st.info("No suggestions available for this campaign yet.")
    else:
        st.dataframe(
            suggestions_df[[
                "campaign_id",
                "campaign_name",
                "targeting",
                "action",
                "confidence",
                "explanation"
            ]],
            column_config={
                "targeting": st.column_config.TextColumn(width=150),
                "action": st.column_config.TextColumn(width=120),
                "confidence": st.column_config.NumberColumn(width=100),
                "explanation": st.column_config.TextColumn(width=900),  # 👈 force wide
            },
            use_container_width=False,
            height=500
        )
        # st.data_editor(
        #     suggestions_df[[
        #         "targeting",
        #         "action",
        #         "confidence",
        #         "explanation"
        #     ]],
        #     use_container_width=False,
        #     height=500,
        #     disabled=True
        # )
    
    st.header("📊 Campaign Performance Summary")

    performance_df = get_campaign_performance_summary()

    # If user selected specific campaign
    if selected_campaign != "All":
        selected_id = campaign_df[
            campaign_df["campaign_name"] == selected_campaign
        ]["campaign_id"].iloc[0]

        performance_df = performance_df[
            performance_df["campaign_id"] == selected_id
        ]

    # Sort by ROAS
    performance_df = performance_df.sort_values("roas", ascending=False)

    st.dataframe(
        performance_df,
        column_config={
            "budget_consumed": st.column_config.NumberColumn(format="₹ %.0f"),
            "sales": st.column_config.NumberColumn(format="₹ %.0f"),
            "spend": st.column_config.NumberColumn(format="₹ %.0f"),
            "roas": st.column_config.NumberColumn(format="%.2f"),
        },
        use_container_width=True,
        height=400
    )