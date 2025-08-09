# app.py
# Run: python -m streamlit run app.py

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from io import BytesIO

# ========================
# Page Configuration
# ========================
st.set_page_config(page_title="📊 Sublimation Cost Calculator", layout="wide")
st.title("📊 Sublimation Cost Calculator")

# ========================
# CSS: smaller KPI numbers
# ========================
st.markdown("""
<style>
/* Main value in KPIs */
div[data-testid="stMetricValue"] {
  font-size: 1.35rem;   /* adjust here if you want smaller/bigger */
  line-height: 1.2;
}
/* KPI label */
div[data-testid="stMetricLabel"] {
  font-size: 0.95rem;
  line-height: 1.2;
}
/* Delta text */
div[data-testid="stMetricDelta"] {
  font-size: 0.95rem;
  line-height: 1.2;
}
</style>
""", unsafe_allow_html=True)

# ---------- Formatting helpers ----------
def fmt_num_en(x, decimals=2):
    try:
        return f"{float(x):,.{decimals}f}"
    except Exception:
        return str(x)

def fmt_int_en(x):
    try:
        return f"{int(round(float(x))):,d}"
    except Exception:
        return str(x)

def fmt_usd(x, decimals=2):
    return f"USD {fmt_num_en(x, decimals)}"

def label_usd_per_m(x):
    return f"{fmt_usd(x)} /m"

# ---------- Sidebar: global options ----------
st.sidebar.header("⚙️ Options")
kpi_cols = st.sidebar.selectbox("KPI columns per row", [3, 4], index=1)
dark_charts = st.sidebar.toggle("Dark charts", value=False)
plotly_template = "plotly_dark" if dark_charts else "plotly"

# =========================
# 1) Production Parameters
# =========================
st.header("1️⃣ Production Parameters & Capacity")
col1, col2, col3 = st.columns(3)
with col1:
    width = st.number_input("Print width (m)", 0.1, 10.0, 1.6, step=0.01, help="Material usable width.")
    speed1 = st.number_input("Speed 1 pass (m/h)", 0.0, 2000.0, 400.0)
    speed2 = st.number_input("Speed 2 passes (m/h)", 0.0, 2000.0, 200.0)

with col2:
    usage1 = st.slider("Usage 1 pass (%)", 0, 100, 50)
    usage2 = 100 - usage1
    st.write(f"Usage 2 passes: **{usage2}%**")

    shifts_per_day = st.number_input("Shifts per day", 1, 4, 1, step=1)
    hours_per_shift = st.number_input("Hours per shift", 1, 12, 8, step=1)
    hours_day = shifts_per_day * hours_per_shift
    st.write(f"Total hours/day: **{hours_day}**")

    days_month = st.number_input("Operating days/month", 1, 31, 24)
    total_hours_month = float(hours_day) * float(days_month)

    downtime_h = st.number_input(
        "Downtime hours per month",
        min_value=0.0, max_value=total_hours_month, value=0.0, step=0.1,
        help="Total hours/month when the machine is NOT producing."
    )

with col3:
    avg_speed = speed1 * usage1/100 + speed2 * usage2/100
    productive_hours = max(0.0, total_hours_month - downtime_h)
    prod_month = avg_speed * productive_hours
    prod_year = prod_month * 12

    st.subheader("📈 Estimated Capacity")
    st.write(f"Monthly production (after downtime): **{fmt_int_en(prod_month)} m**")
    st.write(f"Annual production: **{fmt_int_en(prod_year)} m**")
    if downtime_h > 0:
        lost = avg_speed * downtime_h
        st.warning(f"Downtime **{fmt_num_en(downtime_h,1)} h/mo** reduces ~**{fmt_int_en(lost)} m/mo**.")

utilization = (productive_hours/total_hours_month * 100) if total_hours_month > 0 else 0.0
idle_pct = 100 - utilization

# =========================
# 2) Consumables & Variable Costs
# =========================
st.header("2️⃣ Consumables & Variable Costs")
colv, colc = st.columns(2)
with colv:
    ink_ml = st.number_input("Ink (ml/m)", 0.0, 1000.0, 5.0)
    ink_price_l = st.number_input("Ink price (USD/L)", 0.0, 500.0, 56.7)

    paper_imp_waste = st.number_input("Printing paper waste (%)", 0.0, 20.0, 5.0, step=0.1,
                                      help="Example: 5% ⇒ consumption 1.05 units/m")
    paper_imp_u = 1.0 + paper_imp_waste/100
    st.number_input(
        f"Printing paper (units/m) (consumption = 1 + {paper_imp_waste/100:.2f})",
        value=paper_imp_u, key="paper_imp_display", disabled=True
    )
    paper_imp_price = st.number_input("Printing paper price (USD/unit)", 0.0, 10.0, 0.85)

    paper_prot_waste = st.number_input("Protective paper waste (%)", 0.0, 20.0, 3.0, step=0.1,
                                       help="Example: 3% ⇒ consumption 1.03 units/m")
    paper_prot_u = 1.0 + paper_prot_waste/100
    st.number_input(
        f"Protective paper (units/m) (consumption = 1 + {paper_prot_waste/100:.2f})",
        value=paper_prot_u, key="paper_prot_display", disabled=True
    )
    paper_prot_price = st.number_input("Protective paper price (USD/unit)", 0.0, 10.0, 0.20)

    machine_kw = st.number_input("Machine consumption (kW/h)", 0.0, 1000.0, 60.0)
    elec_price = st.number_input("Electricity price (USD/kWh)", 0.0, 10.0, 1.6)

    # Consumption summaries
    ink_l_month = ink_ml * prod_month / 1000
    ink_l_year = ink_l_month * 12
    paper_imp_month = paper_imp_u * prod_month * width
    paper_imp_year = paper_imp_month * 12
    paper_prot_month = paper_prot_u * prod_month * width
    paper_prot_year = paper_prot_month * 12
    monthly_kwh = machine_kw * productive_hours
    annual_kwh = monthly_kwh * 12

    st.markdown("**Monthly/Annual Consumption**")
    st.write(f"- Ink: **{fmt_num_en(ink_l_month)} L/mo** | **{fmt_num_en(ink_l_year)} L/yr**")
    st.write(f"- Printing paper: **{fmt_int_en(paper_imp_month)} units/mo** | **{fmt_int_en(paper_imp_year)} units/yr**")
    st.write(f"- Protective paper: **{fmt_int_en(paper_prot_month)} units/mo** | **{fmt_int_en(paper_prot_year)} units/yr**")
    st.write(f"- Electricity: **{fmt_int_en(monthly_kwh)} kWh/mo** | **{fmt_int_en(annual_kwh)} kWh/yr**")

with colc:
    cv_ink = ink_ml/1000 * ink_price_l
    cv_paper_imp = paper_imp_u * paper_imp_price
    cv_paper_prot = paper_prot_u * paper_prot_price
    cv_elec = (machine_kw * productive_hours * elec_price) / prod_month if prod_month else 0.0
    cost_var_per_m = cv_ink + cv_paper_imp + cv_paper_prot + cv_elec

    df_var = pd.DataFrame({
        "Item": ["Ink", "Printing paper", "Protective paper", "Electricity", "Total variable"],
        "USD/m": [cv_ink, cv_paper_imp, cv_paper_prot, cv_elec, cost_var_per_m]
    })
    df_var_view = df_var.copy()
    df_var_view["USD/m"] = df_var_view["USD/m"].map(fmt_usd)
    st.table(df_var_view)

# =========================
# 3) Monthly Fixed Costs
# =========================
st.header("3️⃣ Monthly Fixed Costs")
colf1, colf2 = st.columns(2)
with colf1:
    salary = st.number_input("Salaries (USD/month)", 0.0, 100000.0, 25340.0)
    invest_printer = st.number_input("Printer investment (USD)", 0.0, 1e7, 450000.0)
    years_printer = st.number_input("Printer depreciation (years)", 1, 50, 4)
with colf2:
    invest_cal = st.number_input("Calender investment (USD)", 0.0, 1e7, 150000.0)
    years_cal = st.number_input("Calender depreciation (years)", 1, 50, 5)
    rent = st.number_input("Rent (USD/month)", 0.0, 50000.0, 8000.0)
other_fixed = st.number_input("Other fixed costs (USD/month)", 0.0, 100000.0, 0.0)
maintenance = st.number_input("Maintenance (USD/month)", 0.0, 100000.0, 0.0)

depr_printer_m = invest_printer / years_printer / 12
depr_cal_m = invest_cal / years_cal / 12
fixed_cost_month = salary + depr_printer_m + depr_cal_m + rent + other_fixed + maintenance

df_fix = pd.DataFrame({
    "Item": ["Salaries", "Printer depreciation", "Calender depreciation", "Rent", "Other", "Maintenance", "Total"],
    "USD/month": [salary, depr_printer_m, depr_cal_m, rent, other_fixed, maintenance, fixed_cost_month]
})
df_fix_view = df_fix[df_fix["Item"] != "Total"].copy()
df_fix_view["USD/month"] = df_fix_view["USD/month"].map(fmt_usd)
st.table(df_fix_view)

# =========================
# 3.1) Quick KPIs (native)
# =========================
st.header("📌 Quick Summary (KPIs)")
sell_price = st.number_input("Selling price (USD/m)", 0.0, 100.0, 4.5)

revenue_m = sell_price * prod_month
var_total_m = cost_var_per_m * prod_month
profit_m = revenue_m - var_total_m - fixed_cost_month
roi_pct = (profit_m * 12) / (invest_printer + invest_cal) * 100 if (invest_printer + invest_cal) > 0 else 0
BE_m = fixed_cost_month / (sell_price - cost_var_per_m) if sell_price > cost_var_per_m else None
fixed_per_m = (fixed_cost_month / prod_month) if prod_month > 0 else np.nan
total_cost_per_m = cost_var_per_m + (fixed_per_m if pd.notna(fixed_per_m) else 0)
gross_margin_per_m = sell_price - cost_var_per_m
net_margin_per_m = (profit_m / prod_month) if prod_month > 0 else np.nan

# Row 1 of KPIs
row1 = st.columns(kpi_cols)
with row1[0]:
    st.metric("Production (month)", f"{fmt_int_en(prod_month)} m")
with row1[1]:
    if BE_m is not None:
        gap = prod_month - BE_m
        st.metric("Break-even (month)", f"{fmt_int_en(BE_m)} m",
                  delta=f"{'+' if gap >= 0 else ''}{fmt_int_en(gap)} m vs BE")
    else:
        st.metric("Break-even (month)", "—")
with row1[2]:
    st.metric("Profit (month)", fmt_usd(profit_m),
              delta=f"{'+' if profit_m >= 0 else ''}{fmt_usd(profit_m)}")
if kpi_cols == 4:
    with row1[3]:
        st.metric("ROI (annual)", f"{fmt_num_en(roi_pct,1)}%",
                  delta=f"{'+' if roi_pct >= 0 else ''}{fmt_num_en(roi_pct,1)}%")

# Row 2 of KPIs
row2 = st.columns(kpi_cols)
with row2[0]:
    st.metric("Total cost per meter", label_usd_per_m(total_cost_per_m))
with row2[1]:
    st.metric("Gross margin per meter", label_usd_per_m(gross_margin_per_m),
              delta=f"{'+' if gross_margin_per_m>=0 else ''}{label_usd_per_m(gross_margin_per_m)}")
with row2[2]:
    st.metric("Net margin per meter",
              (label_usd_per_m(net_margin_per_m) if pd.notna(net_margin_per_m) else "—"))
if kpi_cols == 4:
    with row2[3]:
        st.metric("Utilization", f"{fmt_num_en(utilization,1)}% (Idle {fmt_num_en(100-utilization,1)}%)")

# =========================
# 4) Charts (2 per row)
# =========================
st.header("4️⃣ Cost Charts")
if prod_month > 0:
    fixed_per_m_series = df_fix[df_fix["Item"] != "Total"].set_index("Item")["USD/month"] / prod_month
    var_series = pd.Series([cv_ink, cv_paper_imp, cv_paper_prot, cv_elec],
                           index=["Ink", "Printing paper", "Protective paper", "Electricity"])

    # Direct vs Indirect (per meter)
    direct_cost = float(var_series.sum())
    indirect_cost = float(fixed_per_m_series.sum())
    fig_ci = go.Figure(data=[
        go.Bar(
            x=["Direct", "Indirect"],
            y=[direct_cost, indirect_cost],
            marker_color=["#66c2a5", "#fc8d62"],
            text=[label_usd_per_m(direct_cost), label_usd_per_m(indirect_cost)],
            textposition="outside",
            textfont=dict(size=13),
            cliponaxis=False,
            width=0.5
        )
    ])
    fig_ci.update_layout(
        template=plotly_template,
        title=dict(text="Direct vs Indirect<br>Costs per Meter", x=0.5, y=0.9, font=dict(size=17)),
        yaxis_title="USD/meter",
        height=300, width=460,
        margin=dict(t=46, b=28, l=36, r=18),
        uniformtext_minsize=12, uniformtext_mode='hide'
    )

    # Fixed per meter
    def fix_label(v):
        pct = (v/fixed_per_m_series.sum()*100) if fixed_per_m_series.sum() else 0
        return f"{label_usd_per_m(v)}<br>({fmt_num_en(pct,1)}%)"

    fig_fix = go.Figure(data=[
        go.Bar(
            y=list(fixed_per_m_series.index),
            x=list(fixed_per_m_series.values),
            orientation="h",
            marker_color="#1f77b4",
            text=[fix_label(v) for v in fixed_per_m_series.values],
            textposition="auto",
            cliponaxis=False
        )
    ])
    fig_fix.update_layout(
        template=plotly_template,
        title=dict(text="Fixed Costs<br>per Meter", x=0.5, y=0.9, font=dict(size=17)),
        xaxis_title="USD/meter",
        height=330, width=500,
        margin=dict(t=46, b=28, l=36, r=18)
    )

    # Variable per meter
    def var_label(v):
        pct = (v/var_series.sum()*100) if var_series.sum() else 0
        return f"{label_usd_per_m(v)}<br>({fmt_num_en(pct,1)}%)"

    fig_var = go.Figure(data=[
        go.Bar(
            y=list(var_series.index),
            x=list(var_series.values),
            orientation="h",
            marker_color="#ff7f0e",
            text=[var_label(v) for v in var_series.values],
            textposition="auto",
            cliponaxis=False
        )
    ])
    fig_var.update_layout(
        template=plotly_template,
        title=dict(text="Variable Costs<br>per Meter", x=0.5, y=0.9, font=dict(size=17)),
        xaxis_title="USD/meter",
        height=330, width=500,
        margin=dict(t=46, b=28, l=36, r=18)
    )

    cA, cB = st.columns(2)
    with cA:
        st.plotly_chart(fig_ci, use_container_width=False)
        st.plotly_chart(fig_fix, use_container_width=False)
    with cB:
        st.plotly_chart(fig_var, use_container_width=False)
else:
    st.warning("Set monthly production > 0 to display charts.")

# =========================
# 5) Summary & ROI (table)
# =========================
st.header("5️⃣ Summary & ROI")
df_sum = pd.DataFrame({
    "Metric": ["Production (m)", "Revenue (USD)", "Variable cost (USD)", "Fixed cost (USD)", "Profit (USD)", "ROI (%)"],
    "Value": [prod_month, sell_price*prod_month, cost_var_per_m*prod_month, fixed_cost_month, profit_m, roi_pct]
}).round(2)
df_sum_view = df_sum.copy()
df_sum_view.loc[df_sum_view["Metric"] == "Production (m)","Value"] = df_sum_view.loc[df_sum_view["Metric"]=="Production (m)","Value"].map(lambda v: f"{fmt_int_en(v)} m")
for m in ["Revenue (USD)", "Variable cost (USD)", "Fixed cost (USD)", "Profit (USD)"]:
    df_sum_view.loc[df_sum_view["Metric"] == m, "Value"] = df_sum_view.loc[df_sum_view["Metric"] == m, "Value"].map(fmt_usd)
df_sum_view.loc[df_sum_view["Metric"] == "ROI (%)", "Value"] = df_sum_view.loc[df_sum_view["Metric"] == "ROI (%)", "Value"].map(lambda v: f"{fmt_num_en(v,1)}%")
st.table(df_sum_view)

# =========================
# 6) Export (CSV + Excel)
# =========================
st.header("6️⃣ Export Reports")
c1, c2, c3, c4 = st.columns(4)
csv_var = df_var.to_csv(index=False).encode("utf-8")
csv_fix = df_fix[df_fix["Item"] != "Total"].to_csv(index=False).encode("utf-8")
csv_sum = df_sum.to_csv(index=False).encode("utf-8")
with c1:
    st.download_button("Variables CSV (USD)", csv_var, file_name="variables.csv")
with c2:
    st.download_button("Fixed CSV (USD)", csv_fix, file_name="fixed.csv")
with c3:
    st.download_button("Summary CSV (USD)", csv_sum, file_name="summary.csv")

with c4:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_var.to_excel(writer, index=False, sheet_name="Variables")
        df_fix.to_excel(writer, index=False, sheet_name="Fixed")
        df_sum.to_excel(writer, index=False, sheet_name="Summary")
        params = {
            "width_m": [width],
            "speed1_mph": [speed1],
            "speed2_mph": [speed2],
            "usage1_%": [usage1],
            "usage2_%": [usage2],
            "shifts_per_day": [shifts_per_day],
            "hours_per_shift": [hours_per_shift],
            "days_month": [days_month],
            "downtime_h": [downtime_h],
            "sell_price_usd_m": [sell_price],
            "prod_month_m": [prod_month],
            "utilization_%": [utilization],
        }
        pd.DataFrame(params).to_excel(writer, index=False, sheet_name="Parameters")
    st.download_button("Download Excel (all tabs)",
                       output.getvalue(),
                       file_name="sublimation_report.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# =========================
# 7) Break-even
# =========================
st.header("7️⃣ Break-even Point")
if sell_price > cost_var_per_m:
    be = fixed_cost_month / (sell_price - cost_var_per_m)
    st.success(
        f"🎯 With selling price **{fmt_usd(sell_price)} /m**, "
        f"you must print **{fmt_int_en(be)} m/month** to avoid losses."
    )
    if prod_month < be:
        st.warning(f"🚩 Current production (**{fmt_int_en(prod_month)} m/month**) is **below BE**.")
    else:
        st.info(f"✅ Current production (**{fmt_int_en(prod_month)} m/month**) is **above BE**.")

    x = np.linspace(0, max(prod_month, be*1.2), 100)
    rev_curve = sell_price * x
    cost_curve = fixed_cost_month + cost_var_per_m * x
    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.plot(x, rev_curve, label="Revenue")
    ax.plot(x, cost_curve, label="Total cost")
    ax.axvline(be, ls="--", label=f"BE: {fmt_int_en(be)} m", color="red")
    ax.set_xlabel("Meters"); ax.set_ylabel("USD"); ax.legend()
    st.pyplot(fig, use_container_width=True)
else:
    if prod_month > 0:
        min_price = (fixed_cost_month / prod_month) + cost_var_per_m
        st.error(
            f"❌ With current production **{fmt_int_en(prod_month)} m/month**, "
            f"minimum price to avoid loss is **{fmt_usd(min_price)} /m**."
        )
    else:
        st.error("❌ Monthly production is zero. Enter positive values.")

# =========================
# 8) Sensitivity Analysis
# =========================
st.header("8️⃣ Sensitivity Analysis")
perc = st.slider("Variation (%)", -50, 50, 10)
be_base = fixed_cost_month / (sell_price - cost_var_per_m) if sell_price > cost_var_per_m else None

def calc_sensitivity(param, base):
    adj = base * (1 + perc/100)
    if param == "ink":
        cv_new = adj/1000 * ink_price_l
        cost_var_new = cv_new + cv_paper_imp + cv_paper_prot + cv_elec
    elif param == "energy":
        kwh_new = adj * productive_hours
        cv_new = kwh_new * elec_price / prod_month if prod_month else 0
        cost_var_new = cv_ink + cv_paper_imp + cv_paper_prot + cv_new
    elif param == "salary":
        cost_var_new = cost_var_per_m
    else:
        cost_var_new = cost_var_per_m

    fixed_new = (adj + depr_printer_m + depr_cal_m + rent + other_fixed + maintenance) if param == "salary" else fixed_cost_month
    profit_new = (sell_price * prod_month) - cost_var_new * prod_month - fixed_new
    roi_new = (profit_new * 12) / (invest_printer + invest_cal) * 100 if (invest_printer + invest_cal) > 0 else 0
    be_new = fixed_new / (sell_price - cost_var_new) if sell_price > cost_var_new else None
    return round(roi_new, 2), (round(be_new, 0) if be_new is not None else None)

params = [
    ("Ink (ml/m)", "ink", ink_ml),
    ("Energy (kW/h)", "energy", machine_kw),
    ("Salaries (USD/month)", "salary", salary)
]
rows = []
for label, key, base in params:
    roi_adj, be_adj = calc_sensitivity(key, base)
    rows.append({
        "Parameter": label,
        "ROI Base (%)": round(roi_pct, 2),
        f"ROI {perc}% (%)": roi_adj,
        "BE Base (m)": round(be_base, 0) if be_base is not None else None,
        f"BE {perc}% (m)": be_adj
    })
df_sens = pd.DataFrame(rows)
df_sens_view = df_sens.copy()
df_sens_view["ROI Base (%)"] = df_sens_view["ROI Base (%)"].map(lambda v: f"{fmt_num_en(v,1)}%")
df_sens_view[f"ROI {perc}% (%)"] = df_sens_view[f"ROI {perc}% (%)"].map(lambda v: f"{fmt_num_en(v,1)}%")
if df_sens_view["BE Base (m)"].notna().any():
    df_sens_view["BE Base (m)"] = df_sens_view["BE Base (m)"].map(lambda v: fmt_int_en(v) if pd.notna(v) else "—")
df_sens_view[f"BE {perc}% (m)"] = df_sens_view[f"BE {perc}% (m)"].map(lambda v: fmt_int_en(v) if v is not None else "—")
st.table(df_sens_view)

# =========================
# 9) What-if Scenarios
# =========================
st.header("9️⃣ What-if Scenarios")
with st.expander("Define alternative scenario"):
    ink_ml_s = st.number_input("Scenario ink (ml/m)", 0.0, 1000.0, ink_ml)
    ink_price_l_s = st.number_input("Scenario ink price (USD/L)", 0.0, 500.0, ink_price_l)

    paper_imp_waste_s = st.number_input("Scenario printing paper waste (%)", 0.0, 20.0, paper_imp_waste, step=0.1)
    paper_imp_u_s = 1.0 + paper_imp_waste_s/100
    st.number_input(
        f"Scenario printing paper (units/m) (consumption = 1 + {paper_imp_waste_s/100:.2f})",
        value=paper_imp_u_s, key="paper_imp_display_s", disabled=True
    )
    paper_imp_price_s = st.number_input("Scenario printing paper price (USD/unit)", 0.0, 10.0, paper_imp_price)

    paper_prot_waste_s = st.number_input("Scenario protective paper waste (%)", 0.0, 20.0, paper_prot_waste, step=0.1)
    paper_prot_u_s = 1.0 + paper_prot_waste_s/100
    st.number_input(
        f"Scenario protective paper (units/m) (consumption = 1 + {paper_prot_waste_s/100:.2f})",
        value=paper_prot_u_s, key="paper_prot_display_s", disabled=True
    )
    paper_prot_price_s = st.number_input("Scenario protective paper price (USD/unit)", 0.0, 10.0, paper_prot_price)

    hours_day_s = st.number_input("Scenario hours/day", 1, 24, int(hours_day))
    days_month_s = st.number_input("Scenario days/month", 1, 31, int(days_month))

    avg_speed_s = speed1 * usage1/100 + speed2 * usage2/100
    prod_month_s = avg_speed_s * hours_day_s * days_month_s

    cv_ink_s = ink_ml_s/1000 * ink_price_l_s
    cv_paper_imp_s = paper_imp_u_s * paper_imp_price_s
    cv_paper_prot_s = paper_prot_u_s * paper_prot_price_s
    monthly_kwh_s = machine_kw * hours_day_s * days_month_s
    cv_elec_s = monthly_kwh_s * elec_price / prod_month_s if prod_month_s else 0
    cost_var_s = cv_ink_s + cv_paper_imp_s + cv_paper_prot_s + cv_elec_s

    revenue_s = sell_price * prod_month_s
    profit_s = revenue_s - cost_var_s * prod_month_s - fixed_cost_month
    roi_s = (profit_s * 12) / (invest_printer + invest_cal) * 100 if (invest_printer + invest_cal) > 0 else 0

    df_scen = pd.DataFrame({
        "Metric": ["Production", "Revenue (USD)", "Variable cost (USD)", "Fixed cost (USD)", "Profit (USD)", "ROI (%)"],
        "Base": [prod_month, sell_price*prod_month, cost_var_per_m*prod_month, fixed_cost_month, profit_m, roi_pct],
        "Scenario": [prod_month_s, revenue_s, cost_var_s*prod_month_s, fixed_cost_month, profit_s, roi_s]
    }).round(2)

    df_scen_view = df_scen.copy()
    df_scen_view.loc[df_scen_view["Metric"]=="Production","Base"] = df_scen_view.loc[df_scen_view["Metric"]=="Production","Base"].map(lambda v: f"{fmt_int_en(v)} m")
    df_scen_view.loc[df_scen_view["Metric"]=="Production","Scenario"] = df_scen_view.loc[df_scen_view["Metric"]=="Production","Scenario"].map(lambda v: f"{fmt_int_en(v)} m")
    for m in ["Revenue (USD)","Variable cost (USD)","Fixed cost (USD)","Profit (USD)"]:
        df_scen_view.loc[df_scen_view["Metric"]==m,"Base"] = df_scen_view.loc[df_scen_view["Metric"]==m,"Base"].map(fmt_usd)
        df_scen_view.loc[df_scen_view["Metric"]==m,"Scenario"] = df_scen_view.loc[df_scen_view["Metric"]==m,"Scenario"].map(fmt_usd)
    df_scen_view.loc[df_scen_view["Metric"]=="ROI (%)","Base"] = df_scen_view.loc[df_scen_view["Metric"]=="ROI (%)","Base"].map(lambda v: f"{fmt_num_en(v,1)}%")
    df_scen_view.loc[df_scen_view["Metric"]=="ROI (%)","Scenario"] = df_scen_view.loc[df_scen_view["Metric"]=="ROI (%)","Scenario"].map(lambda v: f"{fmt_num_en(v,1)}%")
    st.table(df_scen_view)
