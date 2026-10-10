-- HR Employee Attrition Analysis
-- SQL queries for exploring attrition patterns
-- Compatible with SQLite (used via Python's sqlite3 module)

-- ─────────────────────────────────────────
-- 1. Overall attrition rate
-- ─────────────────────────────────────────
SELECT
    Attrition,
    COUNT(*) AS employee_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM employees), 2) AS pct
FROM employees
GROUP BY Attrition;

-- ─────────────────────────────────────────
-- 2. Attrition by Department
-- ─────────────────────────────────────────
SELECT
    Department,
    COUNT(*) AS total,
    SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) AS left_count,
    ROUND(
        SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2
    ) AS attrition_rate_pct
FROM employees
GROUP BY Department
ORDER BY attrition_rate_pct DESC;

-- ─────────────────────────────────────────
-- 3. Attrition by Overtime
-- ─────────────────────────────────────────
SELECT
    OverTime,
    COUNT(*) AS total,
    SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) AS left_count,
    ROUND(
        SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2
    ) AS attrition_rate_pct
FROM employees
GROUP BY OverTime
ORDER BY attrition_rate_pct DESC;

-- ─────────────────────────────────────────
-- 4. Attrition by Job Satisfaction (1=Low, 4=Very High)
-- ─────────────────────────────────────────
SELECT
    JobSatisfaction,
    COUNT(*) AS total,
    SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) AS left_count,
    ROUND(
        SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2
    ) AS attrition_rate_pct
FROM employees
GROUP BY JobSatisfaction
ORDER BY JobSatisfaction;

-- ─────────────────────────────────────────
-- 5. Average monthly income by attrition
-- ─────────────────────────────────────────
SELECT
    Attrition,
    ROUND(AVG(MonthlyIncome), 2) AS avg_monthly_income,
    ROUND(MIN(MonthlyIncome), 2) AS min_income,
    ROUND(MAX(MonthlyIncome), 2) AS max_income
FROM employees
GROUP BY Attrition;

-- ─────────────────────────────────────────
-- 6. Attrition by Years at Company (bucketed)
-- ─────────────────────────────────────────
SELECT
    CASE
        WHEN YearsAtCompany <= 1  THEN '0-1 years'
        WHEN YearsAtCompany <= 3  THEN '2-3 years'
        WHEN YearsAtCompany <= 7  THEN '4-7 years'
        WHEN YearsAtCompany <= 15 THEN '8-15 years'
        ELSE '15+ years'
    END AS tenure_bucket,
    COUNT(*) AS total,
    SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) AS left_count,
    ROUND(
        SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2
    ) AS attrition_rate_pct
FROM employees
GROUP BY tenure_bucket
ORDER BY MIN(YearsAtCompany);

-- ─────────────────────────────────────────
-- 7. Attrition by Job Role
-- ─────────────────────────────────────────
SELECT
    JobRole,
    COUNT(*) AS total,
    SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) AS left_count,
    ROUND(
        SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2
    ) AS attrition_rate_pct
FROM employees
GROUP BY JobRole
ORDER BY attrition_rate_pct DESC;

-- ─────────────────────────────────────────
-- 8. High-risk employee profile
--    (Overtime=Yes, JobSatisfaction <= 2, YearsAtCompany <= 3)
-- ─────────────────────────────────────────
SELECT
    COUNT(*) AS high_risk_count,
    SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) AS actually_left,
    ROUND(
        SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2
    ) AS attrition_rate_pct
FROM employees
WHERE OverTime = 'Yes'
  AND JobSatisfaction <= 2
  AND YearsAtCompany <= 3;