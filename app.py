# app.py
# Para rodar e simular no VS Code:
#   streamlit run app.py

import sys, types
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# Micropip workaround
for mod in ["micropip"]:
    try:
        __import__(mod)
    except ImportError:
        sys.modules[mod] = types.ModuleType(mod)

# === Seletor de Idioma ===
lang = st.sidebar.selectbox(
    "🌐 Selecionar Idioma / Select Language / Seleccionar Idioma",
    ['Português', 'English', 'Español'],
    index=0
)
code = {'Português': 'pt', 'English': 'en', 'Español': 'es'}[lang]

# Traduções de todos os textos
translations = {
    'pt': {
        'title': '📊 Calculadora de Custo para Sublimação',
        'params': '1️⃣ Parâmetros de Produção e Capacidade',
        'capacity': '📈 Capacidade Estimada',
        'cons': '2️⃣ Consumíveis & Custos Variáveis',
        'var_costs': '🔄 Custos Variáveis (USD/m)',
        'fixed': '3️⃣ Custos Fixos Mensais',
        'fix_costs': '🏷️ Custos Fixos',
        'summary': '4️⃣ Resumo Mensal & ROI',
        'sum_sub': '📋 Resumo & ROI',
        'export': '5️⃣ Exportar Relatório (CSV)',
        'export_var': '📥 Variáveis',
        'export_fix': '📥 Fixos',
        'export_sum': '📥 Resumo',
        'be': '6️⃣ Ponto de Equilíbrio',
        'sens': '7️⃣ Análise de Sensibilidade',
        'scenario': '8️⃣ Cenários "E se..."',
        'txt_width': 'Largura da impressão (m)',
        'help_width': 'Largura do material a ser impresso em metros.',
        'txt_vel1': 'Velocidade 1 passada (m/h)',
        'help_vel1': 'Velocidade da primeira passada em metros por hora.',
        'txt_vel2': 'Velocidade 2 passadas (m/h)',
        'help_vel2': 'Velocidade da segunda passada em metros por hora.',
        'txt_usage1': 'Uso 1 passada (%)',
        'help_usage1': 'Percentual de utilização da primeira passada.',
        'txt_hours_day': 'Horas de operação por dia',
        'help_hours_day': 'Número de horas diárias de operação.',
        'txt_days_month': 'Dias de operação por mês',
        'help_days_month': 'Número de dias de operação por mês.',
        'txt_ink_ml': 'Tinta (ml/m)',
        'help_ink_ml': 'Consumo de tinta por metro linear em mililitros.',
        'txt_price_ink_l': 'Preço tinta (USD/L)',
        'help_price_ink_l': 'Preço da tinta por litro em USD.',
        'txt_paper_imp_u': 'Papel impressão (unid/m)',
        'help_paper_imp_u': 'Unidades de papel de impressão por metro linear.',
        'txt_price_paper_imp': 'Preço papel imp. (USD/un)',
        'help_price_paper_imp': 'Preço do papel de impressão por unidade.',
        'txt_paper_prot_u': 'Papel proteção (unid/m)',
        'help_paper_prot_u': 'Unidades de papel de proteção por metro linear.',
        'txt_price_paper_prot': 'Preço papel prot. (USD/un)',
        'help_price_paper_prot': 'Preço do papel de proteção por unidade.',
        'txt_machine_kw': 'Consumo máquina (kW/h)',
        'help_machine_kw': 'Consumo energético da máquina por hora.',
        'txt_price_kw': 'Preço kWh (USD)',
        'help_price_kw': 'Preço da energia elétrica por kWh.',
        'txt_salary': 'Salário (USD/mês)',
        'help_salary': 'Custo de salários mensais.',
        'txt_invest_main': 'Invest. máquina (USD)',
        'help_invest_main': 'Investimento na impressora.',
        'txt_years_main': 'Depreciação máquina (anos)',
        'help_years_main': 'Anos de depreciação da impressora.',
        'txt_invest_cal': 'Invest. calandra (USD)',
        'help_invest_cal': 'Investimento na calandra.',
        'txt_years_cal': 'Depreciação calandra (anos)',
        'help_years_cal': 'Anos de depreciação da calandra.',
        'txt_rent': 'Aluguel (USD/mês)',
        'help_rent': 'Custo de aluguel mensal.',
        'txt_other_fixed': 'Outros fixos (USD)',
        'help_other_fixed': 'Outros custos fixos mensais.',
        'txt_maintenance': 'Manutenção (USD/mês)',
        'help_maintenance': 'Custo de manutenção mensal.',
        'txt_downtime_h': 'Downtime (h/mês)',
        'help_downtime_h': 'Horas de parada mensais.',
        'txt_price_sell': 'Preço venda (USD/m)',
        'help_price_sell': 'Preço de venda por metro.',
        'txt_sens_variation': 'Variação (%)',
        'help_sens_variation': 'Variação percentual para análise de sensibilidade.',
        'expander_scenario': 'Definir Cenário Alternativo',
        'txt_scenario_ink_ml_s': 'Tinta cenário (ml/m)',
        'txt_scenario_price_ink_l_s': 'Preço tinta cenário (USD/L)',
        'txt_scenario_paper_imp_u_s': 'Papel imp. cenário (unid/m)',
        'txt_scenario_price_paper_imp_s': 'Preço papel imp. cenário (USD/un)',
        'txt_scenario_paper_prot_u_s': 'Papel prot. cenário (unid/m)',
        'txt_scenario_price_paper_prot_s': 'Preço papel prot. cenário (USD/un)',
        'txt_scenario_hours_day_s': 'Horas/dia cenário',
        'txt_scenario_days_month_s': 'Dias/mês cenário',
        'var_items': ['Tinta','Papel imp.','Papel prot.','Eletricidade','Total Variável'],
        'var_col_item': 'Insumo',
        'var_col_usd_m': 'USD/m',
        'fix_items': ['Salário','Dep. impr.','Dep. cal.','Aluguel','Outros','Manutenção','Total Fixos'],
        'fix_col_usd_mth': 'USD/mês',
        'fix_col_usd_m': 'USD/m',
        'sum_col_metric': 'Métrica',
        'sum_col_value': 'Valor',
        'sum_metrics': ['Receita','Custo Var.','Custo Fix.','Lucro','ROI (%)'],
        'rev_label': 'Receita',
        'cost_label': 'Custo Total',
        'axis_meters': 'Metros',
        'axis_usd': 'USD',
        'downtime_warn': '⏰ Downtime de {h:.1f}h reduz produção em {m:.0f} m.',
        'be_not_calc': '❌ Preço ≤ custo variável - BE não calculável',
        'prod_above_be': '👍 Produção ({m:.0f} m) acima do BE',
        'prod_at_be': '⚖️ Produção no BE ({m:.0f} m)',
        'prod_below_be': '⚠️ Produção ({m:.0f} m) abaixo do BE'
    },
    'en': {
        'title': '📊 Sublimation Cost Calculator',
        'params': '1️⃣ Production Parameters & Capacity',
        'capacity': '📈 Estimated Capacity',
        'cons': '2️⃣ Consumables & Variable Costs',
        'var_costs': '🔄 Variable Costs (USD/m)',
        'fixed': '3️⃣ Monthly Fixed Costs',
        'fix_costs': '🏷️ Fixed Costs',
        'summary': '4️⃣ Summary & ROI',
        'sum_sub': '📋 Summary & ROI',
        'export': '5️⃣ Export Report (CSV)',
        'export_var': '📥 Variables',
        'export_fix': '📥 Fixed',
        'export_sum': '📥 Summary',
        'be': '6️⃣ Break-even Point',
        'sens': '7️⃣ Sensitivity Analysis',
        'scenario': '8️⃣ "What-if" Scenarios',
        'txt_width': 'Print Width (m)',
        'help_width': 'Width of material to be printed in meters.',
        'txt_vel1': 'Speed 1 pass (m/h)',
        'help_vel1': 'Speed of the first pass in meters per hour.',
        'txt_vel2': 'Speed 2 passes (m/h)',
        'help_vel2': 'Speed of the second pass in meters per hour.',
        'txt_usage1': 'Usage 1 pass (%)',
        'help_usage1': 'Percentage usage of the first pass.',
        'txt_hours_day': 'Operating hours per day',
        'help_hours_day': 'Number of daily operating hours.',
        'txt_days_month': 'Operating days per month',
        'help_days_month': 'Number of operating days per month.',
        'txt_ink_ml': 'Ink (ml/m)',
        'help_ink_ml': 'Ink consumption per linear meter in milliliters.',
        'txt_price_ink_l': 'Ink Price (USD/L)',
        'help_price_ink_l': 'Price of ink per liter in USD.',
        'txt_paper_imp_u': 'Printing Paper (units/m)',
        'help_paper_imp_u': 'Units of printing paper per linear meter.',
        'txt_price_paper_imp': 'Paper Price (USD/unit)',
        'help_price_paper_imp': 'Printing paper price per unit.',
        'txt_paper_prot_u': 'Protection Paper (units/m)',
        'help_paper_prot_u': 'Units of protection paper per linear meter.',
        'txt_price_paper_prot': 'Protection paper price (USD/unit)',
        'help_price_paper_prot': 'Protection paper price per unit.',
        'txt_machine_kw': 'Machine consumption (kW/h)',
        'help_machine_kw': 'Machine energy consumption per hour.',
        'txt_price_kw': 'kWh Price (USD)',
        'help_price_kw': 'Electricity price per kWh.',
        'txt_salary': 'Salary (USD/month)',
        'help_salary': 'Cost of monthly salaries.',
        'txt_invest_main': 'Machine Invest. (USD)',
        'help_invest_main': 'Printer investment.',
        'txt_years_main': 'Machine Depreciation (years)',
        'help_years_main': 'Years of printer depreciation.',
        'txt_invest_cal': 'Calender Invest. (USD)',
        'help_invest_cal': 'Calender investment.',
        'txt_years_cal': 'Calender Depreciation (years)',
        'help_years_cal': 'Years of calender depreciation.',
        'txt_rent': 'Rent (USD/month)',
        'help_rent': 'Monthly rent cost.',
        'txt_other_fixed': 'Other Fixed (USD)',
        'help_other_fixed': 'Other monthly fixed costs.',
        'txt_maintenance': 'Maintenance (USD/month)',
        'help_maintenance': 'Monthly maintenance cost.',
        'txt_downtime_h': 'Downtime (h/month)',
        'help_downtime_h': 'Monthly downtime hours.',
        'txt_price_sell': 'Selling Price (USD/m)',
        'help_price_sell': 'Selling price per meter.',
        'txt_sens_variation': 'Variation (%)',
        'help_sens_variation': 'Percentage variation for sensitivity analysis.',
        'expander_scenario': 'Define Alternative Scenario',
        'txt_scenario_ink_ml_s': 'Scenario ink (ml/m)',
        'txt_scenario_price_ink_l_s': 'Scenario ink price (USD/L)',
        'txt_scenario_paper_imp_u_s': 'Scenario paper units (units/m)',
        'txt_scenario_price_paper_imp_s': 'Scenario paper price (USD/unit)',
        'txt_scenario_paper_prot_u_s': 'Scenario protection units (units/m)',
        'txt_scenario_price_paper_prot_s': 'Scenario protection price (USD/unit)',
        'txt_scenario_hours_day_s': 'Scenario hours/day',
        'txt_scenario_days_month_s': 'Scenario days/month',
        'var_items': ['Ink', 'Print Paper', 'Protection Paper', 'Electricity', 'Total Variable'],
        'var_col_item': 'Item',
        'var_col_usd_m': 'USD/m',
        'fix_items': ['Salary', 'Printer Dep.', 'Calender Dep.', 'Rent', 'Others', 'Maintenance', 'Total Fixed'],
        'fix_col_usd_mth': 'USD/month',
        'fix_col_usd_m': 'USD/m',
        'sum_col_metric': 'Metric',
        'sum_col_value': 'Value',
        'sum_metrics': ['Revenue', 'Var Cost', 'Fixed Cost', 'Profit', 'ROI (%)'],
        'rev_label': 'Revenue',
        'cost_label': 'Total Cost',
        'axis_meters': 'Meters',
        'axis_usd': 'USD',
        'downtime_warn': '⏰ Downtime of {h:.1f}h reduces production by {m:.0f} m.',
        'be_not_calc': '❌ Price ≤ variable cost - BE not calculable',
        'prod_above_be': '👍 Production ({m:.0f} m) above BE',
        'prod_at_be': '⚖️ Production at BE ({m:.0f} m)',
        'prod_below_be': '⚠️ Production ({m:.0f} m) below BE'
    },
    'es': {
        'title': '📊 Calculadora de Costos para Sublimación',
        'params': '1️⃣ Parámetros de Producción y Capacidad',
        'capacity': '📈 Capacidad Estimada',
        'cons': '2️⃣ Consumibles y Costos Variables',
        'var_costs': '🔄 Costos Variables (USD/m)',
        'fixed': '3️⃣ Costos Fijos Mensuales',
        'fix_costs': '🏷️ Costos Fijos',
        'summary': '4️⃣ Resumen Mensual y ROI',
        'sum_sub': '📋 Resumen y ROI',
        'export': '5️⃣ Exportar Informe (CSV)',
        'export_var': '📥 Variables',
        'export_fix': '📥 Fijos',
        'export_sum': '📥 Resumen',
        'be': '6️⃣ Punto de Equilibrio',
        'sens': '7️⃣ Análisis de Sensibilidad',
        'scenario': '8️⃣ Escenarios "Y si..."',
        'txt_width': 'Ancho de impresión (m)',
        'help_width': 'Ancho del material a imprimir en metros.',
        'txt_vel1': 'Velocidad 1 pasada (m/h)',
        'help_vel1': 'Velocidad de la primera pasada en metros por hora.',
        'txt_vel2': 'Velocidad 2 pasadas (m/h)',
        'help_vel2': 'Velocidad de la segunda pasada en metros por hora.',
        'txt_usage1': 'Uso 1 pasada (%)',
        'help_usage1': 'Porcentaje de uso de la primera pasada.',
        'txt_hours_day': 'Horas de operación por día',
        'help_hours_day': 'Número de horas diarias de operación.',
        'txt_days_month': 'Días de operación por mes',
        'help_days_month': 'Número de días de operación por mes.',
        'txt_ink_ml': 'Tinta (ml/m)',
        'help_ink_ml': 'Consumo de tinta por metro lineal en mililitros.',
        'txt_price_ink_l': 'Precio tinta (USD/L)',
        'help_price_ink_l': 'Precio de la tinta por litro en USD.',
        'txt_paper_imp_u': 'Papel de impresión (unid/m)',
        'help_paper_imp_u': 'Unidades de papel de impresión por metro lineal.',
        'txt_price_paper_imp': 'Precio papel imp. (USD/un)',
        'help_price_paper_imp': 'Precio del papel de impresión por unidad.',
        'txt_paper_prot_u': 'Papel de protección (unid/m)',
        'help_paper_prot_u': 'Unidades de papel de protección por metro lineal.',
        'txt_price_paper_prot': 'Precio papel prot. (USD/un)',
        'help_price_paper_prot': 'Precio del papel de protección por unidad.',
        'txt_machine_kw': 'Consumo máquina (kW/h)',
        'help_machine_kw': 'Consumo energético de la máquina por hora.',
        'txt_price_kw': 'Precio kWh (USD)',
        'help_price_kw': 'Precio de electricidad por kWh.',
        'txt_salary': 'Salario (USD/mes)',
        'help_salary': 'Costo de salarios mensuales.',
        'txt_invest_main': 'Inversión máquina (USD)',
        'help_invest_main': 'Inversión en la impresora.',
        'txt_years_main': 'Depreciación máquina (años)',
        'help_years_main': 'Años de depreciación de la impresora.',
        'txt_invest_cal': 'Inversión calandra (USD)',
        'help_invest_cal': 'Inversión en la calandra.',
        'txt_years_cal': 'Depreciación calandra (años)',
        'help_years_cal': 'Años de depreciación de la calandra.',
        'txt_rent': 'Alquiler (USD/mes)',
        'help_rent': 'Costo mensual de alquiler.',
        'txt_other_fixed': 'Otros fijos (USD)',
        'help_other_fixed': 'Otros costos fijos mensuales.',
        'txt_maintenance': 'Mantenimiento (USD/mes)',
        'help_maintenance': 'Costo mensual de mantenimiento.',
        'txt_downtime_h': 'Tiempo inactividad (h/mes)',
        'help_downtime_h': 'Horas de parada mensuales.',
        'txt_price_sell': 'Precio de venta (USD/m)',
        'help_price_sell': 'Precio de venta por metro.',
        'txt_sens_variation': 'Variación (%)',
        'help_sens_variation': 'Variación porcentual para el análisis de sensibilidad.',
        'expander_scenario': 'Definir Escenario Alternativo',
        'txt_scenario_ink_ml_s': 'Tinta escenario (ml/m)',
        'txt_scenario_price_ink_l_s': 'Precio tinta escenario (USD/L)',
        'txt_scenario_paper_imp_u_s': 'Papel imp. escenario (unid/m)',
        'txt_scenario_price_paper_imp_s': 'Precio papel imp. escenario (USD/un)',
        'txt_scenario_paper_prot_u_s': 'Papel prot. escenario (unid/m)',
        'txt_scenario_price_paper_prot_s': 'Precio papel prot. escenario (USD/un)',
        'txt_scenario_hours_day_s': 'Horas/día escenario',
        'txt_scenario_days_month_s': 'Días/mes escenario',
        'var_items': ['Tinta','Papel de impresión','Papel de protección','Electricidad','Total Variable'],
        'var_col_item': 'Insumo',
        'var_col_usd_m': 'USD/m',
        'fix_items': ['Salario','Dep. impr.','Dep. cal.','Alquiler','Otros','Mantenimiento','Total Fijos'],
        'fix_col_usd_mth': 'USD/mes',
        'fix_col_usd_m': 'USD/m',
        'sum_col_metric': 'Métrica',
        'sum_col_value': 'Valor',
        'sum_metrics': ['Ingresos','Costo Var.','Costo Fijo','Beneficio','ROI (%)'],
        'rev_label': 'Ingresos',
        'cost_label': 'Costo Total',
        'axis_meters': 'Metros',
        'axis_usd': 'USD',
        'downtime_warn': '⏰ Tiempo de inactividad de {h:.1f}h reduce la producción en {m:.0f} m.',
        'be_not_calc': '❌ Precio ≤ costo variable - BE no calculable',
        'prod_above_be': '👍 Producción ({m:.0f} m) por encima del BE',
        'prod_at_be': '⚖️ Producción en BE ({m:.0f} m)',
        'prod_below_be': '⚠️ Producción ({m:.0f} m) por debajo del BE'
    }
}
trans = translations[code]

# === Configuração da página ===
st.set_page_config(page_title=trans['title'], layout="wide")
st.title(trans['title'])

# === 1️⃣ Parâmetros de Produção e Capacidade ===
st.header(trans['params'])
col1, col2, col3 = st.columns(3)
with col1:
    largura = st.number_input(
        trans['txt_width'], 0.1, 10.0, 1.6, step=0.01,
        help=trans['help_width']
    )
    vel1 = st.number_input(
        trans['txt_vel1'], 0.0, 2000.0, 400.0,
        help=trans['help_vel1']
    )
    vel2 = st.number_input(
        trans['txt_vel2'], 0.0, 2000.0, 200.0,
        help=trans['help_vel2']
    )
with col2:
    uso1 = st.slider(
        trans['txt_usage1'], 0, 100, 50,
        help=trans['help_usage1']
    )
    uso2 = 100 - uso1
    st.write(f"{trans['txt_usage1'].replace('1','2')}: {uso2}%")
    hours_day = st.number_input(
        trans['txt_hours_day'], 1, 24, 8,
        help=trans['help_hours_day']
    )
    days_month = st.number_input(
        trans['txt_days_month'], 1, 31, 24,
        help=trans['help_days_month']
    )
with col3:
    vel_med = vel1 * uso1 / 100 + vel2 * uso2 / 100
    prod_month = vel_med * hours_day * days_month
    prod_year = prod_month * 12
    st.subheader(trans['capacity'])
    st.write(f"{trans['capacity'].split()[-1]} mensal: {prod_month:,.0f} m")
    st.write(f"{trans['capacity'].split()[-1]} anual: {prod_year:,.0f} m")

# === 2️⃣ Consumíveis & Custos Variáveis ===
st.header(trans['cons'])
colv, colc = st.columns(2)
with colv:
    ink_ml = st.number_input(
        trans['txt_ink_ml'], 0.0, 1000.0, 5.0,
        help=trans['help_ink_ml']
    )
    price_ink_l = st.number_input(
        trans['txt_price_ink_l'], 0.0, 500.0, 56.7,
        help=trans['help_price_ink_l']
    )
    paper_imp_u = st.number_input(
        trans['txt_paper_imp_u'], 0.0, 10.0, 1.05,
        help=trans['help_paper_imp_u']
    )
    price_paper_imp = st.number_input(
        trans['txt_price_paper_imp'], 0.0, 10.0, 0.85,
        help=trans['help_price_paper_imp']
    )
    paper_prot_u = st.number_input(
        trans['txt_paper_prot_u'], 0.0, 10.0, 0.5,
        help=trans['help_paper_prot_u']
    )
    price_paper_prot = st.number_input(
        trans['txt_price_paper_prot'], 0.0, 10.0, 0.20,
        help=trans['help_price_paper_prot']
    )
    machine_kw = st.number_input(
        trans['txt_machine_kw'], 0.0, 1000.0, 60.0,
        help=trans['help_machine_kw']
    )
    price_kw = st.number_input(
        trans['txt_price_kw'], 0.0, 10.0, 1.6,
        help=trans['help_price_kw']
    )
    # consumos mensal/ano
    ink_l_month = ink_ml * prod_month / 1000
    ink_l_year = ink_l_month * 12
    paper_imp_month = paper_imp_u * prod_month * largura
    paper_imp_year = paper_imp_month * 12
    paper_prot_month = paper_prot_u * prod_month * largura
    paper_prot_year = paper_prot_month * 12
    monthly_kwh = machine_kw * hours_day * days_month
    annual_kwh = monthly_kwh * 12
    st.markdown("**Consumos Mensal/Anual**")
    st.write(f"- Tinta: {ink_l_month:.2f} L/mês | {ink_l_year:.2f} L/ano")
    st.write(f"- Papel imp.: {paper_imp_month:.0f} un/mês | {paper_imp_year:.0f} un/ano")
    st.write(f"- Papel prot.: {paper_prot_month:.0f} un/mês | {paper_prot_year:.0f} un/ano")
    st.write(f"- Energia: {monthly_kwh:.0f} kWh/mês | {annual_kwh:.0f} kWh/ano")
with colc:
    cv_ink = ink_ml / 1000 * price_ink_l
    cv_paper_imp = paper_imp_u * price_paper_imp
    cv_paper_prot = paper_prot_u * price_paper_prot
    cv_elec = (monthly_kwh * price_kw) / prod_month if prod_month else 0
    cost_var_meter = cv_ink + cv_paper_imp + cv_paper_prot + cv_elec
    df_var = pd.DataFrame({
        trans['var_col_item']: trans['var_items'],
        trans['var_col_usd_m']: [cv_ink, cv_paper_imp, cv_paper_prot, cv_elec, cost_var_meter]
    })
    st.subheader(trans['var_costs'])
    st.table(df_var.style.format({trans['var_col_usd_m']: '{:.2f}'}))

# === 3️⃣ Custos Fixos Mensais ===
st.header(trans['fixed'])
colf1, colf2 = st.columns(2)
with colf1:
    salary = st.number_input(
        trans['txt_salary'], 0.0, 100000.0, 25340.0,
        help=trans['help_salary']
    )
    invest_main = st.number_input(
        trans['txt_invest_main'], 0.0, 1e7, 450000.0,
        help=trans['help_invest_main']
    )
    years_main = st.number_input(
        trans['txt_years_main'], 1, 50, 4,
        help=trans['help_years_main']
    )
with colf2:
    invest_cal = st.number_input(
        trans['txt_invest_cal'], 0.0, 1e7, 150000.0,
        help=trans['help_invest_cal']
    )
    years_cal = st.number_input(
        trans['txt_years_cal'], 1, 50, 5,
        help=trans['help_years_cal']
    )
    rent = st.number_input(
        trans['txt_rent'], 0.0, 50000.0, 8000.0,
        help=trans['help_rent']
    )
other_fixed = st.number_input(
    trans['txt_other_fixed'], 0.0, 100000.0, 0.0,
    help=trans['help_other_fixed']
)
maintenance = st.number_input(
    trans['txt_maintenance'], 0.0, 100000.0, 0.0,
    help=trans['help_maintenance']
)
downtime_h = st.number_input(
    trans['txt_downtime_h'], 0.0, 200.0, 0.0,
    help=trans['help_downtime_h']
)
# cálculos fixos
depr_main_m = invest_main / years_main / 12
depr_cal_m = invest_cal / years_cal / 12
cost_fix_m = salary + depr_main_m + depr_cal_m + rent + other_fixed + maintenance
lost_prod = downtime_h * vel_med
if downtime_h:
    st.warning(trans['downtime_warn'].format(h=downtime_h, m=lost_prod))
_df_fix = pd.DataFrame({
    trans['var_col_item']: trans['fix_items'],
    trans['fix_col_usd_mth']: [salary, depr_main_m, depr_cal_m, rent, other_fixed, maintenance, cost_fix_m],
    trans['fix_col_usd_m']: [x / prod_month for x in [salary, depr_main_m, depr_cal_m, rent, other_fixed, maintenance, cost_fix_m]]
})
st.subheader(trans['fix_costs'])
st.table(_df_fix.style.format({
    trans['fix_col_usd_mth']: '{:.0f}',
    trans['fix_col_usd_m']: '{:.2f}'
}))

# === 4️⃣ Resumo & ROI ===
st.header(trans['summary'])
price_sell = st.number_input(
    trans['txt_price_sell'], 0.0, 100.0, 4.5,
    help=trans['help_price_sell']
)
revenue_m = price_sell * prod_month
cost_var_m = cost_var_meter * prod_month
profit_m = revenue_m - cost_var_m - cost_fix_m
roi = (profit_m * 12) / (invest_main + invest_cal) * 100 if (invest_main + invest_cal) > 0 else 0
_df_sum = pd.DataFrame({
    trans['sum_col_metric']: trans['sum_metrics'],
    trans['sum_col_value']: [revenue_m, cost_var_m, cost_fix_m, profit_m, roi]
}).round(2)
st.subheader(trans['sum_sub'])
st.table(_df_sum)

# === 5️⃣ Exportar Relatório (CSV) ===
st.header(trans['export'])
colx1, colx2, colx3 = st.columns(3)
csv1 = df_var.to_csv(index=False).encode('utf-8')
csv2 = _df_fix.to_csv(index=False).encode('utf-8')
csv3 = _df_sum.to_csv(index=False).encode('utf-8')
with colx1:
    st.download_button(trans['export_var'], csv1)
with colx2:
    st.download_button(trans['export_fix'], csv2)
with colx3:
    st.download_button(trans['export_sum'], csv3)

# === 6️⃣ Ponto de Equilíbrio ===
st.header(trans['be'])
if price_sell > cost_var_meter:
    be = cost_fix_m / (price_sell - cost_var_meter)
    st.subheader(f"📈 BE: {be:,.0f} m")
    x = np.linspace(0, max(prod_month, be * 1.2), 100)
    rev_curve = price_sell * x
    cost_curve = cost_fix_m + cost_var_meter * x
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(x, rev_curve, label=trans['rev_label'])
    ax.plot(x, cost_curve, label=trans['cost_label'])
    ax.axvline(be, ls='--', label=f"BE: {be:,.0f} m")
    ax.set_xlabel(trans['axis_meters'])
    ax.set_ylabel(trans['axis_usd'])
    ax.legend()
    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)
    if prod_month > be:
        st.success(trans['prod_above_be'].format(m=prod_month))
    elif abs(prod_month - be) < 1:
        st.info(trans['prod_at_be'].format(m=be))
    else:
        st.warning(trans['prod_below_be'].format(m=prod_month))
else:
    st.error(trans['be_not_calc'])

# === 7️⃣ Análise de Sensibilidade ===
st.header(trans['sens'])
perc = st.slider(
    trans['txt_sens_variation'], -50, 50, 10,
    help=trans['help_sens_variation']
)
def sens(param, base):
    val = base * (1 + perc / 100)
    if param == 'tinta':
        cv_new = val / 1000 * price_ink_l
        cost_var_new = cv_new + cv_paper_imp + cv_paper_prot + cv_elec
        fix_new = cost_fix_m
    elif param == 'energia':
        monthly_kwh_new = val * hours_day * days_month
        cv_new = (monthly_kwh_new * price_kw) / prod_month if prod_month else 0
        cost_var_new = cv_ink + cv_paper_imp + cv_paper_prot + cv_new
        fix_new = cost_fix_m
    else:
        fix_new = val + depr_main_m + depr_cal_m + rent + other_fixed + maintenance
        cost_var_new = cost_var_meter
    profit_new = revenue_m - cost_var_new * prod_month - fix_new
    roi_new = (profit_new * 12) / (invest_main + invest_cal) * 100 if (invest_main + invest_cal) > 0 else 0
    be_new = fix_new / (price_sell - cost_var_new) if price_sell > cost_var_new else None
    return roi_new, be_new

rows = []
for p, key in [(trans['var_items'][0], 'tinta'), (trans['var_items'][3], 'energia'), (trans['fix_items'][0], 'salário')]:
    base = {'tinta': ink_ml, 'energia': machine_kw, 'salário': salary}[key]
    r, b_new = sens(key, base)
    rows.append({
        trans['var_col_item']: p,
        'ROI Base (%)': roi,
        f'ROI {perc}% (%)': r,
        'BE Base (m)': be,
        f'BE {perc}% (m)': b_new
    })
df_sens = pd.DataFrame(rows).round(2)
st.table(df_sens)

# === 8️⃣ Cenários "E se..." ===
st.header(trans['scenario'])
with st.expander(trans['expander_scenario']):
    ink_ml_s = st.number_input(trans['txt_scenario_ink_ml_s'], 0.0, 1000.0, ink_ml)
    price_ink_l_s = st.number_input(trans['txt_scenario_price_ink_l_s'], 0.0, 500.0, price_ink_l)
    paper_imp_u_s = st.number_input(trans['txt_scenario_paper_imp_u_s'], 0.0, 10.0, paper_imp_u)
    price_paper_imp_s = st.number_input(trans['txt_scenario_price_paper_imp_s'], 0.0, 10.0, price_paper_imp)
    paper_prot_u_s = st.number_input(trans['txt_scenario_paper_prot_u_s'], 0.0, 10.0, paper_prot_u)
    price_paper_prot_s = st.number_input(trans['txt_scenario_price_paper_prot_s'], 0.0, 10.0, price_paper_prot)
    hours_day_s = st.number_input(trans['txt_scenario_hours_day_s'], 1, 24, hours_day)
    days_month_s = st.number_input(trans['txt_scenario_days_month_s'], 1, 31, days_month)
    vel_med_s = vel1 * uso1 / 100 + vel2 * uso2 / 100
    prod_month_s = vel_med_s * hours_day_s * days_month_s
    # (Continue com os cálculos e exibição do cenário conforme necessidade)
