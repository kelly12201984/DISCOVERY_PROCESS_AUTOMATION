-- ============================================================
-- PO STATUS BY JOB (DETAIL)
-- Every BOM line on every active job, with PO and receipt info
-- For all active jobs from 2024-present
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

    -- PO Header
    ph.PO AS PO_Number,
    ph.Vendor AS PO_Vendor,
    v.Name AS Vendor_Name,
    ph.Order_Date AS PO_Order_Date,
    ph.Status AS PO_Status,

    -- PO Detail (line item)
    pd.Line AS PO_Line,
    pd.Order_Quantity AS PO_Qty_Ordered,
    pd.Unit_Cost AS PO_Unit_Cost,
    pd.Due_Date AS PO_Due_Date,
    pd.Status AS PO_Line_Status,
    pd.Vendor_Reference,

    -- Receipt info from Material_Trans
    (SELECT SUM(mt.Quantity)
     FROM Material_Trans mt
     WHERE mt.Material_Req = mr.Material_Req
       AND mt.Tran_Type = 'R'
    ) AS Total_Qty_Received,

    (SELECT MAX(mt.Material_Trans_Date)
     FROM Material_Trans mt
     WHERE mt.Material_Req = mr.Material_Req
       AND mt.Tran_Type = 'R'
    ) AS Last_Receipt_Date,

    -- Calculated status flag
    CASE
        WHEN mr.Pick_Buy_Indicator = 'P' THEN 'PICK FROM STOCK'
        WHEN ph.PO IS NULL THEN 'NO PO CREATED'
        WHEN ISNULL(mr.Act_Qty, 0) >= mr.Est_Qty THEN 'FULLY RECEIVED'
        WHEN ISNULL(mr.Act_Qty, 0) > 0 THEN 'PARTIAL ('
            + CAST(CAST(mr.Act_Qty AS INT) AS VARCHAR)
            + '/' + CAST(CAST(mr.Est_Qty AS INT) AS VARCHAR) + ')'
        WHEN pd.Due_Date < GETDATE() THEN 'OVERDUE - Due '
            + CONVERT(VARCHAR(10), pd.Due_Date, 101)
        ELSE 'ON ORDER - Due '
            + CONVERT(VARCHAR(10), pd.Due_Date, 101)
    END AS Receipt_Status

FROM Job j
INNER JOIN Material_Req mr ON mr.Job = j.Job
LEFT JOIN PO_Detail pd ON pd.Holder_ID = CAST(mr.Material_Req AS VARCHAR)
LEFT JOIN PO_Header ph ON ph.PO = pd.PO
LEFT JOIN Vendor v ON v.Vendor = ph.Vendor

WHERE j.Status IN ('Active', 'Hold')
  AND j.Order_Date >= '2024-01-01'
  AND mr.Pick_Buy_Indicator = 'B'

ORDER BY j.Job, mr.Due_Date, mr.Material
