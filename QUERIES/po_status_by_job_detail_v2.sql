-- ============================================================
-- PO STATUS BY JOB (DETAIL) — FIXED JOIN
-- Uses Material_Trans to link POs to Material Requirements
-- instead of Holder_ID (which returns no matches)
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

    -- PO info via Material_Trans linkage
    po_link.PO_Number,
    po_link.Vendor_Name,
    po_link.PO_Order_Date,
    po_link.PO_Status,
    po_link.PO_Due_Date,
    po_link.Total_Qty_Received,
    po_link.Last_Receipt_Date,

    -- Calculated status flag
    CASE
        WHEN mr.Pick_Buy_Indicator = 'P' THEN 'PICK FROM STOCK'
        WHEN mr.Status = 'C' AND ISNULL(mr.Act_Qty, 0) >= mr.Est_Qty THEN 'FULLY RECEIVED'
        WHEN po_link.PO_Number IS NOT NULL AND ISNULL(mr.Act_Qty, 0) >= mr.Est_Qty THEN 'FULLY RECEIVED'
        WHEN po_link.PO_Number IS NOT NULL AND ISNULL(mr.Act_Qty, 0) > 0 THEN 'PARTIAL ('
            + CAST(CAST(mr.Act_Qty AS INT) AS VARCHAR)
            + '/' + CAST(CAST(mr.Est_Qty AS INT) AS VARCHAR) + ')'
        WHEN po_link.PO_Number IS NOT NULL AND po_link.PO_Due_Date < GETDATE() THEN 'OVERDUE - Due '
            + CONVERT(VARCHAR(10), po_link.PO_Due_Date, 101)
        WHEN po_link.PO_Number IS NOT NULL THEN 'ON ORDER - Due '
            + CONVERT(VARCHAR(10), po_link.PO_Due_Date, 101)
        WHEN mr.Status = 'C' THEN 'CLOSED (no PO found)'
        ELSE 'NO PO CREATED'
    END AS Receipt_Status

FROM Job j
INNER JOIN Material_Req mr ON mr.Job = j.Job

-- Join PO data through Material_Trans (the receiving table)
LEFT JOIN (
    SELECT
        mt.Material_Req,
        mt.PO_Number,
        v.Name AS Vendor_Name,
        ph.Order_Date AS PO_Order_Date,
        ph.Status AS PO_Status,
        ph.Due_Date AS PO_Due_Date,
        SUM(mt.Quantity) AS Total_Qty_Received,
        MAX(mt.Material_Trans_Date) AS Last_Receipt_Date
    FROM Material_Trans mt
    LEFT JOIN PO_Header ph ON ph.PO = mt.PO_Number
    LEFT JOIN Vendor v ON v.Vendor = ph.Vendor
    WHERE mt.Material_Req IS NOT NULL
      AND mt.Material_Req > 0
    GROUP BY mt.Material_Req, mt.PO_Number, v.Name,
             ph.Order_Date, ph.Status, ph.Due_Date
) po_link ON po_link.Material_Req = mr.Material_Req

WHERE j.Status IN ('Active', 'Hold')
  AND j.Order_Date >= '2024-01-01'
  AND mr.Pick_Buy_Indicator = 'B'

ORDER BY j.Job, mr.Due_Date, mr.Material
