-- ============================================================
-- DIAGNOSTIC V3: Based on Data Dictionary findings
-- Holder_ID is E_Synergy (dead field). Need the REAL PO-to-Job link.
-- Run each query separately.
-- ============================================================


-- QUERY 1: Material_Trans with Tran_Type = 'R' (Receipt from PO)
-- Our earlier test only showed 'Issue' types. Receipts may have PO data.
SELECT TOP 30
    Material_Trans,
    Material_Req,
    PO_Number,
    PO_Line,
    Job,
    Material,
    Tran_Type,
    Quantity,
    Unit_Cost,
    Material_Trans_Date,
    Description
FROM Material_Trans
WHERE Tran_Type IN ('R', 'Receipt', 'Recv')
ORDER BY Material_Trans_Date DESC


-- QUERY 2: What Tran_Types exist in Material_Trans?
SELECT Tran_Type, COUNT(*) AS Cnt
FROM Material_Trans
GROUP BY Tran_Type
ORDER BY Cnt DESC


-- QUERY 3: Material_Trans rows that DO have PO_Number populated
SELECT TOP 30
    Material_Trans,
    Material_Req,
    PO_Number,
    PO_Line,
    Job,
    Material,
    Vendor,
    Tran_Type,
    Quantity,
    Unit_Cost,
    Material_Trans_Date
FROM Material_Trans
WHERE PO_Number IS NOT NULL
  AND LEN(PO_Number) > 0
ORDER BY Material_Trans_Date DESC


-- QUERY 4: Is there a Source table?
SELECT TOP 20 * FROM Source ORDER BY 1 DESC


-- QUERY 5: The Data Dictionary mentions "Source records" for PO_Detail.
-- Check if there's a table that links PO_Detail to Material_Req directly.
-- Try: does Material_Req have a PO_Detail column we missed?
SELECT TOP 10
    Material_Req,
    Job,
    Material,
    Vendor,
    Description,
    Status,
    Est_Qty,
    Act_Qty
FROM Material_Req
WHERE Job = '25-101'
  AND Act_Qty > 0
