-- ============================================================
-- QUICK TEST: Does ObjectID-to-Holder_ID join work?
-- Run this FIRST before running the full v3 query
-- Should return PO numbers if the join is correct
-- ============================================================

-- Test 1: Check what ObjectID looks like on Material_Req
SELECT TOP 10
    mr.Material_Req,
    mr.ObjectID,
    mr.Job,
    mr.Material,
    mr.Description,
    mr.Act_Qty,
    mr.Status
FROM Material_Req mr
WHERE mr.Job = '25-101'
  AND mr.Act_Qty > 0

-- Test 2: Try the GUID join
SELECT TOP 20
    mr.Job,
    mr.Material,
    mr.ObjectID AS MR_ObjectID,
    pd.Holder_ID AS PD_Holder_ID,
    pd.PO,
    pd.Line,
    pd.Order_Quantity,
    pd.Due_Date,
    ph.Vendor,
    v.Name
FROM Material_Req mr
INNER JOIN PO_Detail pd ON pd.Holder_ID = CAST(mr.ObjectID AS VARCHAR(38))
INNER JOIN PO_Header ph ON ph.PO = pd.PO
LEFT JOIN Vendor v ON v.Vendor = ph.Vendor
WHERE mr.Job IN ('25-101', '25-055', '24-046')

-- Test 3: If Test 2 returns nothing, the GUID format might differ
-- Check the actual formats side by side
SELECT TOP 5 'Material_Req' AS Source, CAST(ObjectID AS VARCHAR(38)) AS GUID_Value
FROM Material_Req WHERE ObjectID IS NOT NULL
UNION ALL
SELECT TOP 5 'PO_Detail', Holder_ID
FROM PO_Detail WHERE Holder_ID IS NOT NULL AND Holder_ID != ''
