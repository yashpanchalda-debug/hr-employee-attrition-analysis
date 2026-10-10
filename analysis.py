"""
HR Employee Attrition Analysis
================================
Loads IBM HR dataset, runs SQL queries via SQLite,
generates visualizations, and exports an Excel summary.

Usage:
    python analysis.py

Requirements:
    pip install pandas matplotlib seaborn openpyxl

Dataset:
    WA_Fn-UseC_-HR-Employee-Attrition.csv  (place in project root)
    https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset
"""

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ── Configuration ────────────────────────────────────────────
DATA_FILE = "WA_Fn-UseC_-HR-Employee-Attrition.csv"
EXCEL_OUTPUT = "attrition_summary.xlsx"
sns.set_theme(style="whitegrid", palette="muted")

# ── 1. Load Data ─────────────────────────────────────────────
print("Loading dataset...")
if not os.path.exists(DATA_FILE):
    raise FileNotFoundError(
        f"Dataset not found: {DATA_FILE}\n"
        "Download from: https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset"
    )

df = pd.read_csv(DATA_FILE)
print(f"  Rows: {len(df):,}  |  Columns: {len(df.columns)}")

# ── 2. Basic Cleaning ─────────────────────────────────────────
# Convert Attrition to binary for numeric calculations
df["Attrited"] = (df["Attrition"] == "Yes").astype(int)

# Drop columns with no variance (common in this dataset)
cols_to_drop = [c for c in ["EmployeeCount", "Over18", "StandardHours"] if c in df.columns]
df.drop(columns=cols_to_drop, inplace=True)

print(f"  Attrition rate: {df['Attrited'].mean()*100:.1f}%")

# ── 3. Load into SQLite ───────────────────────────────────────
print("\nLoading data into in-memory SQLite...")
conn = sqlite3.connect(":memory:")
df.to_sql("employees", conn, index=False, if_exists="replace")

def run_query(sql):
    return pd.read_sql_query(sql, conn)

# ── 4. SQL Analysis ───────────────────────────────────────────

print("\n--- Overall Attrition ---")
q1 = run_query("""
    SELECT Attrition,
           COUNT(*) AS count,
           ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM employees), 1) AS pct
    FROM employees
    GROUP BY Attrition
""")
print(q1.to_string(index=False))

print("\n--- Attrition by Department ---")
q_dept = run_query("""
    SELECT Department,
           COUNT(*) AS total,
           SUM(Attrited) AS left_count,
           ROUND(SUM(Attrited) * 100.0 / COUNT(*), 1) AS attrition_pct
    FROM employees
    GROUP BY Department
    ORDER BY attrition_pct DESC
""")
print(q_dept.to_string(index=False))

print("\n--- Attrition by Overtime ---")
q_ot = run_query("""
    SELECT OverTime,
           COUNT(*) AS total,
           SUM(Attrited) AS left_count,
           ROUND(SUM(Attrited) * 100.0 / COUNT(*), 1) AS attrition_pct
    FROM employees
    GROUP BY OverTime
    ORDER BY attrition_pct DESC
""")
print(q_ot.to_string(index=False))

print("\n--- Attrition by Job Satisfaction ---")
q_sat = run_query("""
    SELECT JobSatisfaction,
           COUNT(*) AS total,
           SUM(Attrited) AS left_count,
           ROUND(SUM(Attrited) * 100.0 / COUNT(*), 1) AS attrition_pct
    FROM employees
    GROUP BY JobSatisfaction
    ORDER BY JobSatisfaction
""")
print(q_sat.to_string(index=False))

print("\n--- Average Income by Attrition ---")
q_income = run_query("""
    SELECT Attrition,
           ROUND(AVG(MonthlyIncome), 0) AS avg_income,
           ROUND(MIN(MonthlyIncome), 0) AS min_income,
           ROUND(MAX(MonthlyIncome), 0) AS max_income
    FROM employees
    GROUP BY Attrition
""")
print(q_income.to_string(index=False))

print("\n--- Attrition by Tenure ---")
q_tenure = run_query("""
    SELECT
        CASE
            WHEN YearsAtCompany <= 1  THEN '0-1 yrs'
            WHEN YearsAtCompany <= 3  THEN '2-3 yrs'
            WHEN YearsAtCompany <= 7  THEN '4-7 yrs'
            WHEN YearsAtCompany <= 15 THEN '8-15 yrs'
            ELSE '15+ yrs'
        END AS tenure_bucket,
        COUNT(*) AS total,
        SUM(Attrited) AS left_count,
        ROUND(SUM(Attrited) * 100.0 / COUNT(*), 1) AS attrition_pct
    FROM employees
    GROUP BY tenure_bucket
    ORDER BY MIN(YearsAtCompany)
""")
print(q_tenure.to_string(index=False))

print("\n--- High-Risk Profile (OT + Low Satisfaction + New) ---")
q_risk = run_query("""
    SELECT COUNT(*) AS group_size,
           SUM(Attrited) AS actually_left,
           ROUND(SUM(Attrited) * 100.0 / COUNT(*), 1) AS attrition_pct
    FROM employees
    WHERE OverTime = 'Yes'
      AND JobSatisfaction <= 2
      AND YearsAtCompany <= 3
""")
print(q_risk.to_string(index=False))

# ── 5. Visualizations ─────────────────────────────────────────
print("\nGenerating charts...")

# Chart 1: Attrition by Department
fig, ax = plt.subplots(figsize=(7, 4))
bars = ax.barh(q_dept["Department"], q_dept["attrition_pct"], color=["#e74c3c","#e67e22","#3498db"])
ax.set_xlabel("Attrition Rate (%)")