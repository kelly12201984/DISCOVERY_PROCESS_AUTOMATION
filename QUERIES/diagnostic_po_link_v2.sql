-- ============================================================
-- DIAGNOSTIC: Find how POs link to Jobs
-- The GUID join doesn't work. Let's find the actual link.
-- Run each query separately in SSMS
-- ============================================================


-- QUERY 1: PO_Detail has an Ext_Description field (text)
-- Maybe the job number is stored there?
SELECT TOP 30
    pd.PO,
    pd.Line,
    pd.Holder_ID,
    pd.Ext_Description,
    pd.Note_Text,
    pd.Order_Quantity,
    pd.Unit_Cost,
    pd.Due_Date,
    pd.Status,
    ph.Vendor,
    v.Name
FROM PO_Detail pd
JOIN PO_Header ph ON ph.PO = pd.PO
LEFT JOIN Vendor v ON v.Vendor = ph.Vendor
WHERE ph.Order_Date >= '2025-01-01'
  AND pd.Status IN ('Open', 'Closed')
ORDER BY ph.Order_Date DESC


-- QUERY 2: Material_Trans is the receiving table.
-- It has BOTH PO_Number and Job columns.
-- But our earlier test showed them as NULL.
-- Let's check if ANY Material_Trans rows have PO data at all.
SELECT TOP 30
    PO_Number,
    PO_Line,
    Job,
    Material,
    Material_Req,
    Tran_Type,
    Quantity,
    Unit_Cost,
    Material_Trans_Date,
    Description
FROM Material_Trans
WHERE PO_Number IS NOT NULL
  AND PO_Number != ''
ORDER BY Material_Trans_Date DESC


-- QUERY 3: If Material_Trans has no PO data, try the other direction.
-- Find POs for a KNOWN vendor+material combo.
-- Job 25-101 has Material "PLT 304L 1/2 X 48 X" from Material_Req.
-- Search PO_Detail for that description.
SELECT
    pd.PO,
    pd.Line,
    pd.Ext_Description,
    pd.Order_Quantity,
    pd.Unit_Cost,
    pd.Due_Date,
    pd.Status,
    ph.Vendor,
    v.Name,
    ph.Order_Date,
    ph.Comment
FROM PO_Detail pd
JOIN PO_Header ph ON ph.PO = pd.PO
LEFT JOIN Vendor v ON v.Vendor = ph.Vendor
WHERE pd.Ext_Description LIKE '%304L%1/2%'
  AND ph.Order_Date >= '2025-06-01'
ORDER BY ph.Order_Date DESC


-- QUERY 4: Check if Holder_ID matches Job_Operation.ObjectID instead
SELECT TOP 10
    pd.PO,
    pd.Line,
    pd.Holder_ID,
    jo.ObjectID AS JO_ObjectID,
    jo.Job,
    jo.Sequence,
    jo.Description
FROM PO_Detail pd
INNER JOIN Job_Operation jo ON pd.Holder_ID = '{' + CAST(jo.ObjectID AS VARCHAR(36)) + '}'
WHERE pd.PO = 'RECO3765'


-- QUERY 5: Just show me the Holder_ID GUID owners.
-- Try matching against ALL tables with ObjectID.
-- Start with Job.ObjectID
SELECT TOP 5
    pd.PO,
    pd.Holder_ID,
    j.Job,
    j.Description
FROM PO_Detail pd
INNER JOIN Job j ON pd.Holder_ID = '{' + CAST(j.ObjectID AS VARCHAR(36)) + '}'
WHERE pd.PO = 'RECO3765'
