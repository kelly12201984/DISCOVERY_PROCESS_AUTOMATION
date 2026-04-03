-- ============================================================
-- JOB MATERIAL SUMMARY — VERTIV ONLY
-- Run in SSMS against PRODUCTION on DC2
-- ============================================================

SELECT
    j.Job,
    j.Customer,
    j.Description,
    j.Status,
    j.Order_Date,

    COUNT(mr.Material_Req) AS Total_BOM_Lines,
    SUM(CASE WHEN mr.Pick_Buy_Indicator = 'B' THEN 1 ELSE 0 END) AS Buy_Items,
    SUM(CASE WHEN mr.Pick_Buy_Indicator = 'P' THEN 1 ELSE 0 END) AS Pick_Items,

    SUM(mr.Est_Total_Cost) AS Est_Material_Cost,
    SUM(mr.Act_Total_Cost) AS Act_Material_Cost,

    SUM(CASE WHEN mr.Status = 'C' THEN 1 ELSE 0 END) AS Lines_Closed,
    SUM(CASE WHEN mr.Status = 'O' AND mr.Pick_Buy_Indicator = 'B' THEN 1 ELSE 0 END) AS Lines_Open,
    SUM(CASE WHEN mr.Pick_Buy_Indicator = 'B'
              AND ISNULL(mr.Act_Qty, 0) >= mr.Est_Qty THEN 1 ELSE 0 END) AS Lines_Fully_Received,
    SUM(CASE WHEN mr.Pick_Buy_Indicator = 'B'
              AND ISNULL(mr.Act_Qty, 0) > 0
              AND ISNULL(mr.Act_Qty, 0) < mr.Est_Qty THEN 1 ELSE 0 END) AS Lines_Partial,
    SUM(CASE WHEN mr.Pick_Buy_Indicator = 'B'
              AND ISNULL(mr.Act_Qty, 0) = 0 THEN 1 ELSE 0 END) AS Lines_Nothing_Received,

    CASE WHEN SUM(CASE WHEN mr.Pick_Buy_Indicator = 'B' THEN 1 ELSE 0 END) = 0 THEN 100
         ELSE CAST(
            SUM(CASE WHEN mr.Pick_Buy_Indicator = 'B'
                      AND ISNULL(mr.Act_Qty, 0) >= mr.Est_Qty THEN 1 ELSE 0 END) * 100.0
            / SUM(CASE WHEN mr.Pick_Buy_Indicator = 'B' THEN 1 ELSE 0 END)
         AS DECIMAL(5,1))
    END AS Pct_Materials_Received

FROM Job j
INNER JOIN Material_Req mr ON mr.Job = j.Job
WHERE j.Status IN ('Active', 'Hold')
  AND j.Order_Date >= '2024-01-01'
  AND j.Customer = 'VERTCORP'
GROUP BY j.Job, j.Customer, j.Description, j.Status, j.Order_Date
ORDER BY Pct_Materials_Received ASC, j.Job
