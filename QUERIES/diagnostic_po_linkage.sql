-- ============================================================
-- DIAGNOSTIC: How does Material_Trans actually link to things?
-- Run each of these separately in SSMS to find the right join
-- ============================================================

-- QUERY 1: What does Material_Trans look like for a KNOWN received item?
-- Pick a job we know has received material (Act_Qty > 0)
SELECT TOP 20
    mr.Job,
    mr.Material,
    mr.Material_Req,
    mr.Act_Qty,
    mr.Status,
    mt.Material_Trans,
    mt.PO_Number,
    mt.PO_Line,
    mt.Quantity,
    mt.Tran_Type,
    mt.Material_Trans_Date,
    mt.Material_Req AS MT_Material_Req,
    mt.Job AS MT_Job
FROM Material_Req mr
INNER JOIN Material_Trans mt ON mt.Job = mr.Job AND mt.Material = mr.Material
WHERE mr.Job IN ('25-101', '25-055', '24-046')
  AND mr.Act_Qty > 0
ORDER BY mr.Job, mr.Material


-- QUERY 2: Does Material_Trans.Material_Req field actually contain values?
SELECT TOP 100
    Material_Trans,
    Material_Req,
    PO_Number,
    PO_Line,
    Job,
    Material,
    Tran_Type,
    Quantity,
    Material_Trans_Date
FROM Material_Trans
WHERE Job IN ('25-101', '25-055', '24-046')
ORDER BY Material_Trans_Date DESC


-- QUERY 3: Simple - just show me PO_Detail for a known job
-- We know POs exist (12,044 of them). Let's find ones for these jobs.
SELECT
    pd.PO,
    pd.Line,
    pd.Status,
    pd.Order_Quantity,
    pd.Unit_Cost,
    pd.Due_Date,
    pd.Holder_ID,
    pd.Ext_Description,
    ph.Vendor,
    v.Name AS Vendor_Name,
    ph.Order_Date
FROM PO_Detail pd
JOIN PO_Header ph ON ph.PO = pd.PO
LEFT JOIN Vendor v ON v.Vendor = ph.Vendor
WHERE pd.Ext_Description LIKE '%25-101%'
   OR pd.Ext_Description LIKE '%25-055%'
   OR pd.Note_Text LIKE '%25-101%'
   OR ph.Comment LIKE '%25-101%'
ORDER BY pd.PO, pd.Line


-- QUERY 4: What's in Holder_ID? Is it empty, or does it contain something unexpected?
SELECT TOP 50
    PO,
    Line,
    Holder_ID,
    Ext_Description,
    Order_Quantity,
    Unit_Cost,
    Status
FROM PO_Detail
WHERE Holder_ID IS NOT NULL
  AND Holder_ID != ''
ORDER BY PO DESC


-- QUERY 5: Does Material_Trans.Material_Req ever have non-null values?
SELECT TOP 20
    Material_Req,
    PO_Number,
    Job,
    Material,
    Tran_Type,
    Quantity
FROM Material_Trans
WHERE Material_Req IS NOT NULL
  AND Material_Req > 0
ORDER BY Material_Trans_Date DESC
