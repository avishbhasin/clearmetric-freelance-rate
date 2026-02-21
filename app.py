"""
Freelance Rate Calculator — Free Web Tool by ClearMetric
https://clearmetric.gumroad.com

Helps freelancers figure out their hourly/project rate based on target income,
expenses, taxes, and billable hours.
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Freelance Rate Calculator — ClearMetric",
    page_icon="💰",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Custom CSS (navy theme)
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    .main .block-container { padding-top: 2rem; max-width: 1200px; }
    .stMetric { background: #f8f9fa; border-radius: 8px; padding: 12px; border-left: 4px solid #1a5276; }
    h1 { color: #1a5276; }
    h2, h3 { color: #2c3e50; }
    .cta-box {
        background: linear-gradient(135deg, #1a5276 0%, #2e86c1 100%);
        color: white; padding: 24px; border-radius: 12px; text-align: center;
        margin: 20px 0;
    }
    .cta-box a { color: #f0d78c; text-decoration: none; font-weight: bold; font-size: 1.1rem; }
    div[data-testid="stSidebar"] { background: #f8f9fa; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown("# 💰 Freelance Rate Calculator")
st.markdown("**Figure out your hourly and project rates** — based on your target income, expenses, and billable hours.")
st.markdown("---")

# ---------------------------------------------------------------------------
# Sidebar — User inputs
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## Your Numbers")

    st.markdown("### Income & Expenses")
    target_annual = st.number_input("Target Annual Income ($)", value=80_000, min_value=0, step=5_000, format="%d")
    annual_expenses = st.number_input("Annual Business Expenses ($)", value=5_000, min_value=0, step=500, format="%d",
                                     help="Software, tools, coworking, etc.")
    self_employment_tax = st.slider("Self-Employment Tax Rate (%)", 0.0, 25.0, 15.3, 0.5) / 100
    income_tax_rate = st.slider("Effective Income Tax Rate (%)", 0.0, 50.0, 22.0, 1.0) / 100

    st.markdown("### Benefits & Savings")
    health_insurance = st.number_input("Health Insurance ($/month)", value=500, min_value=0, step=50, format="%d")
    retirement_pct = st.slider("Retirement Savings (% of income)", 0.0, 30.0, 10.0, 1.0) / 100

    st.markdown("### Time Off")
    vacation_weeks = st.number_input("Vacation Weeks/Year", value=4, min_value=0, max_value=52, step=1)
    sick_days = st.number_input("Sick/Personal Days/Year", value=10, min_value=0, max_value=365, step=1)
    holidays = st.number_input("Holidays/Year", value=10, min_value=0, max_value=30, step=1)

    st.markdown("### Billable Hours")
    billable_hours_day = st.number_input("Billable Hours/Day", value=6.0, min_value=0.5, max_value=12.0, step=0.5,
                                        help="Not all 8 hours are billable — admin, meetings, etc.")
    days_per_week = st.number_input("Days/Week", value=5, min_value=1, max_value=7, step=1)

    st.markdown("### Margin")
    profit_margin = st.slider("Desired Profit Margin (%)", 0.0, 50.0, 20.0, 1.0) / 100

# ---------------------------------------------------------------------------
# Core calculations
# ---------------------------------------------------------------------------
# Non-billable days
sick_holiday_weeks = (sick_days + holidays) / 5  # assume 5-day week
total_off_weeks = vacation_weeks + sick_holiday_weeks
billable_weeks = max(52 - total_off_weeks, 1)
billable_hours_year = billable_weeks * days_per_week * billable_hours_day

if billable_hours_year <= 0:
    billable_hours_year = 1

# Annual costs
annual_health = health_insurance * 12
retirement_amount = target_annual * retirement_pct
# Taxes on (target + retirement + 1/2 SE tax): simplified
taxable_base = target_annual + retirement_amount + (target_annual * 0.5 * self_employment_tax)  # rough
income_tax = taxable_base * income_tax_rate
se_tax = target_annual * self_employment_tax  # simplified
total_taxes = income_tax + se_tax

total_annual_costs = total_taxes + annual_health + retirement_amount + annual_expenses

# Revenue needed
total_revenue_needed = target_annual + total_annual_costs
# Add profit margin
revenue_with_margin = total_revenue_needed / (1 - profit_margin) if profit_margin < 1 else total_revenue_needed

# Rates
min_hourly = total_revenue_needed / billable_hours_year
hourly_recommended = revenue_with_margin / billable_hours_year
hourly_premium = hourly_recommended * 1.5

# Day rate (billable hours per day)
day_rate_min = min_hourly * billable_hours_day
day_rate_rec = hourly_recommended * billable_hours_day
day_rate_premium = hourly_premium * billable_hours_day

# Monthly retainer (4.33 weeks)
billable_hours_month = billable_hours_year / 12
monthly_retainer_min = min_hourly * billable_hours_month
monthly_retainer_rec = hourly_recommended * billable_hours_month
monthly_retainer_premium = hourly_premium * billable_hours_month

# Salary equivalent: your take-home = equivalent to this W-2 salary (with benefits)
salary_equivalent = target_annual

# ---------------------------------------------------------------------------
# Display — Key metrics
# ---------------------------------------------------------------------------
st.markdown("## Key Results")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Recommended Hourly Rate", f"${hourly_recommended:,.0f}", help="Covers income, costs, and profit margin")
m2.metric("Day Rate", f"${day_rate_rec:,.0f}", help=f"Based on {billable_hours_day} billable hours/day")
m3.metric("Monthly Retainer", f"${monthly_retainer_rec:,.0f}", help="~4.33 weeks/month")
m4.metric("Salary Equivalent", f"${salary_equivalent:,.0f}", help="Your take-home ≈ this W-2 salary with benefits")

with st.expander("📊 Calculation Summary", expanded=False):
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Total Annual Costs", f"${total_annual_costs:,.0f}", "Taxes + insurance + retirement + expenses")
        st.metric("Total Revenue Needed", f"${total_revenue_needed:,.0f}", "Income + costs")
    with c2:
        st.metric("Billable Weeks/Year", f"{billable_weeks:.1f}", f"52 - {total_off_weeks:.1f} off")
        st.metric("Billable Hours/Year", f"{billable_hours_year:,.0f}", f"{billable_hours_day} hrs/day × {days_per_week} days")
    with c3:
        st.metric("Minimum Hourly Rate", f"${min_hourly:,.0f}", "Before profit margin")
        st.metric("Revenue (with margin)", f"${revenue_with_margin:,.0f}", f"Includes {profit_margin*100:.0f}% margin")

st.markdown("---")

# ---------------------------------------------------------------------------
# Pie chart: Where your revenue goes
# ---------------------------------------------------------------------------
st.markdown("## Where Your Revenue Goes")

take_home = target_annual
revenue_breakdown = {
    "Take-Home": take_home,
    "Income Tax": income_tax,
    "Self-Employment Tax": se_tax,
    "Health Insurance": annual_health,
    "Retirement": retirement_amount,
    "Business Expenses": annual_expenses,
    "Profit Margin": revenue_with_margin - total_revenue_needed,
}
# Filter out zero/negative
revenue_breakdown = {k: max(0, v) for k, v in revenue_breakdown.items() if v > 0}
total_pie = sum(revenue_breakdown.values())
if total_pie > 0:
    fig_pie = go.Figure(data=[go.Pie(
        labels=list(revenue_breakdown.keys()),
        values=list(revenue_breakdown.values()),
        hole=0.4,
        marker_colors=["#1a5276", "#2e86c1", "#5dade2", "#27ae60", "#f39c12", "#e74c3c", "#9b59b6"],
        textinfo="percent+label",
        textposition="outside",
    )])
    fig_pie.update_layout(
        height=400,
        showlegend=True,
        legend=dict(orientation="h", y=1.02),
        margin=dict(t=40, b=40),
        template="plotly_white",
    )
    st.plotly_chart(fig_pie, use_container_width=True)
else:
    st.info("Adjust inputs to see revenue breakdown.")

st.markdown("---")

# ---------------------------------------------------------------------------
# Rate comparison table
# ---------------------------------------------------------------------------
st.markdown("## Rate Comparison")

rate_df = pd.DataFrame({
    "Tier": ["Minimum", "Recommended", "Premium (1.5x)"],
    "Hourly Rate": [min_hourly, hourly_recommended, hourly_premium],
    "Day Rate": [day_rate_min, day_rate_rec, day_rate_premium],
    "Monthly Retainer": [monthly_retainer_min, monthly_retainer_rec, monthly_retainer_premium],
})
st.dataframe(
    rate_df.style.format({
        "Hourly Rate": "${:,.0f}",
        "Day Rate": "${:,.0f}",
        "Monthly Retainer": "${:,.0f}",
    }, subset=["Hourly Rate", "Day Rate", "Monthly Retainer"]),
    use_container_width=True,
    hide_index=True,
)

st.markdown("---")

# ---------------------------------------------------------------------------
# Project rate calculator
# ---------------------------------------------------------------------------
st.markdown("## Project Pricer")

proj_col1, proj_col2 = st.columns(2)
with proj_col1:
    project_hours = st.number_input("Project Hours", value=40, min_value=0, step=5, format="%d")
    suggested_price = project_hours * hourly_recommended

with proj_col2:
    st.metric("Suggested Project Price", f"${suggested_price:,.0f}")
    st.caption(f"At ${hourly_recommended:,.0f}/hr × {project_hours} hours")

st.markdown("---")

# ---------------------------------------------------------------------------
# "If client offers $X/hour" calculator
# ---------------------------------------------------------------------------
st.markdown("## Client Offer Calculator")

client_offer = st.number_input("If a client offers ($/hour)", value=100, min_value=0, step=10, format="%d")
if client_offer > 0:
    gross_from_offer = client_offer * billable_hours_year
    # Apply same cost structure (simplified)
    tax_on_offer = gross_from_offer * (income_tax_rate + self_employment_tax)
    retirement_on_offer = gross_from_offer * retirement_pct
    costs_on_offer = tax_on_offer + annual_health + retirement_on_offer + annual_expenses
    take_home_from_offer = gross_from_offer - costs_on_offer
    if gross_from_offer > 0:
        effective_rate = take_home_from_offer / billable_hours_year
        st.metric("Your Actual Take-Home (Annual)", f"${take_home_from_offer:,.0f}")
        st.caption(f"After taxes, insurance, retirement, expenses. Effective rate: ${effective_rate:,.0f}/hr")
        if take_home_from_offer < target_annual:
            st.warning(f"⚠️ This offer yields ${target_annual - take_home_from_offer:,.0f} less than your target.")
        else:
            st.success(f"✓ This offer meets your target (${take_home_from_offer - target_annual:,.0f} above).")

st.markdown("---")

# ---------------------------------------------------------------------------
# CTA — Paid Excel
# ---------------------------------------------------------------------------
st.markdown("""
<div class="cta-box">
    <h3 style="color: white; margin: 0 0 8px 0;">Want the Full Excel Spreadsheet?</h3>
    <p style="margin: 0 0 16px 0;">
        Get the <strong>ClearMetric Freelance Rate Calculator</strong> — a downloadable Excel template with:<br>
        ✓ All inputs in one place with gold input cells<br>
        ✓ Project Pricer sheet with line items for quotes<br>
        ✓ Revenue breakdown and rate comparison<br>
        ✓ How To Use guide
    </p>
    <a href="https://clearmetric.gumroad.com" target="_blank">
        Get It on Gumroad — $11.99 →
    </a>
</div>
""", unsafe_allow_html=True)

# Cross-sell
st.markdown("### More from ClearMetric")
cx1, cx2, cx3 = st.columns(3)
with cx1:
    st.markdown("""
    **📋 Freelancer Tax Planner** — $14.99
    Estimate quarterly taxes, deductions, and self-employment tax.
    [Get it →](https://clearmetric.gumroad.com)
    """)
with cx2:
    st.markdown("""
    **📊 Budget Planner** — $13.99
    Track income, expenses, savings with the 50/30/20 framework.
    [Get it →](https://clearmetric.gumroad.com)
    """)
with cx3:
    st.markdown("""
    **🔥 FIRE Calculator** — $14.99
    Find your FIRE number, scenario comparison, year-by-year projection.
    [Get it →](https://clearmetric.gumroad.com)
    """)

# Footer
st.markdown("---")
st.caption("© 2026 ClearMetric | [clearmetric.gumroad.com](https://clearmetric.gumroad.com) | "
           "This tool is for educational purposes only. Not financial advice. Consult a qualified financial advisor.")
