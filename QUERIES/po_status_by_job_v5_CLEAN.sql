-- ============================================================
-- PO STATUS BY JOB — CLEAN VERSION (V5)
-- Removed: Job_Status, Pick_Buy_Indicator, Certs_Required,
--          Lead_Days, Source_Recv_Qty, PO_Line, PO_Line_Status, PO_Status
-- Added: Column headers via column aliases
--
-- Run in SSMS against PRODUCTION on DC2
-- To export with headers: Query > Results To > Results to File,
-- or right-click results > Save Results As > CSV
-- ============================================================

SELECT
    j.Job                                                AS [Job],
    j.Customer                                           AS [Customer],
    j.Description                                        AS [Job Description],
    j.Order_Date                                         AS [Order Date],

    mr.Material                                          AS [Material],
    mr.Description                                       AS [Material Description],
    mr.Est_Qty                                           AS [Qty Needed],
    mr.Act_Qty                                           AS [Qty Received],
    mr.Est_Qty - ISNULL(mr.Act_Qty, 0)                  AS [Qty Outstanding],
    mr.Est_Unit_Cost                                     AS [Unit Cost],
    mr.Est_Total_Cost                                    AS [Total Cost],
    mr.Vendor                                            AS [BOM Vendor],
    mr.Due_Date                                          AS [Material Due Date],
    mr.Status                                            AS [Material Status],

    ph.PO                                                AS [PO Number],
    v.Name                                               AS [Vendor Name],
    ph.Order_Date                                        AS [PO Order Date],
    pd.Order_Quantity                                    AS [PO Qty Ordered],
    pd.Unit_Cost                                         AS [PO Unit Cost],
    pd.Due_Date                                          AS [PO Due Date],
    src.Last_Recv_Date                                   AS [Last Receipt Date],

    CASE
        WHEN ph.PO IS NOT NULL AND ISNULL(mr.Act_Qty, 0) >= mr.Est_Qty
            THEN 'FULLY RECEIVED'
        WHEN ph.PO IS NOT NULL AND ISNULL(mr.Act_Qty, 0) > 0
            THEN 'PARTIAL ('
                + CAST(CAST(mr.Act_Qty AS INT) AS VARCHAR)
                + '/' + CAST(CAST(mr.Est_Qty AS INT) AS VARCHAR) + ')'
        WHEN ph.PO IS NOT NULL AND pd.Due_Date < GETDATE()
            THEN 'OVERDUE - Due ' + CONVERT(VARCHAR(10), pd.Due_Date, 101)
        WHEN ph.PO IS NOT NULL
            THEN 'ON ORDER - Due ' + CONVERT(VARCHAR(10), pd.Due_Date, 101)
        WHEN mr.Status = 'C' AND ISNULL(mr.Act_Qty, 0) >= mr.Est_Qty
            THEN 'RECEIVED (no PO link)'
        WHEN mr.Status = 'C'
            THEN 'CLOSED'
        ELSE 'NO PO CREATED'
    END                                                  AS [Status]

FROM Job j
INNER JOIN Material_Req mr ON mr.Job = j.Job
LEFT JOIN Source src ON src.Material_Req = mr.Material_Req
LEFT JOIN PO_Detail pd ON pd.PO_Detail = src.PO_Detail
LEFT JOIN PO_Header ph ON ph.PO = pd.PO
LEFT JOIN Vendor v ON v.Vendor = ph.Vendor

WHERE j.Status IN ('Active', 'Hold')
  AND j.Order_Date >= '2024-01-01'
  AND mr.Pick_Buy_Indicator = 'B'

ORDER BY j.Job, mr.Due_Date, mr.Material
