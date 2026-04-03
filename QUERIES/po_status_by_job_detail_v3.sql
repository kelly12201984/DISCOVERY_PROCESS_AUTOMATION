-- ============================================================
-- PO STATUS BY JOB (DETAIL) — V3 FIXED
-- Joins PO_Detail.Holder_ID (GUID) to Material_Req.ObjectID (GUID)
--
-- Run in SSMS against PRODUCTION on DC2
-- ============================================================

SELECT
    j.Job,
    j.Customer,
    j.Description AS Job_Description,
    j.Status AS Job_Status,
    j.Order_Date,

    -- Material requirement (BOM line)
    mr.Material,
    mr.Description AS Material_Description,
    mr.Est_Qty AS Qty_Needed,
    mr.Act_Qty AS Qty_Received,
    mr.Est_Qty - ISNULL(mr.Act_Qty, 0) AS Qty_Outstanding,
    mr.Est_Unit_Cost,
    mr.Est_Total_Cost,
    mr.Pick_Buy_Indicator,
    mr.Vendor AS BOM_Vendor,
    mr.Due_Date AS Material_Due_Date,
    mr.Lead_Days,
    mr.Certs_Required,
    mr.Status AS Material_Status,

    -- PO info (joined via GUID)
    ph.PO AS PO_Number,
    v.Name AS Vendor_Name,
    ph.Order_Date AS PO_Order_Date,
    ph.Status AS PO_Status,
    pd.Line AS PO_Line,
    pd.Order_Quantity AS PO_Qty_Ordered,
    pd.Unit_Cost AS PO_Unit_Cost,
    pd.Due_Date AS PO_Due_Date,
    pd.Status AS PO_Line_Status,

    -- Calculated status flag
    CASE
        WHEN mr.Pick_Buy_Indicator = 'P' THEN 'PICK FROM STOCK'
        WHEN ph.PO IS NOT NULL AND ISNULL(mr.Act_Qty, 0) >= mr.Est_Qty THEN 'FULLY RECEIVED'
        WHEN ph.PO IS NOT NULL AND ISNULL(mr.Act_Qty, 0) > 0 THEN 'PARTIAL ('
            + CAST(CAST(mr.Act_Qty AS INT) AS VARCHAR)
            + '/' + CAST(CAST(mr.Est_Qty AS INT) AS VARCHAR) + ')'
        WHEN ph.PO IS NOT NULL AND pd.Due_Date < GETDATE() THEN 'OVERDUE - Due '
            + CONVERT(VARCHAR(10), pd.Due_Date, 101)
        WHEN ph.PO IS NOT NULL THEN 'ON ORDER - Due '
            + CONVERT(VARCHAR(10), pd.Due_Date, 101)
        WHEN mr.Status = 'C' AND ISNULL(mr.Act_Qty, 0) >= mr.Est_Qty THEN 'FULLY RECEIVED (no PO link)'
        WHEN mr.Status = 'C' THEN 'CLOSED (no PO link)'
        ELSE 'NO PO CREATED'
    END AS Receipt_Status

FROM Job j
INNER JOIN Material_Req mr ON mr.Job = j.Job
LEFT JOIN PO_Detail pd ON pd.Holder_ID = CAST(mr.ObjectID AS VARCHAR(38))
LEFT JOIN PO_Header ph ON ph.PO = pd.PO
LEFT JOIN Vendor v ON v.Vendor = ph.Vendor

WHERE j.Status IN ('Active', 'Hold')
  AND j.Order_Date >= '2024-01-01'
  AND mr.Pick_Buy_Indicator = 'B'

ORDER BY j.Job, mr.Due_Date, mr.Material
