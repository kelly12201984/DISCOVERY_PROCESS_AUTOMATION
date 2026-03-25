<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# YES

```markdown
# JobBOSS 18.2 XML SDK – PO Automation Summary

## Core Facts

- JobBOSS 18.2 = legacy on‑prem JobBOSS (not JobBOSS²).
- Official integration: XML SDK via COM object `JBRequestProcessor`.
- No documented `PurchaseOrderAddRq`; POs are driven indirectly via jobs/materials and JobBOSS’s purchasing module.

---

## Supported Objects (Relevant to POs)

- Vendor: `VendorAddRq`, `VendorModRq`, `VendorDelRq`, `VendorQueryRq`, `VendorListQueryRq`
- Material: `MaterialAddRq`, `MaterialModRq`, `MaterialDelRq`, `MaterialQueryRq`, `MaterialListQueryRq`
- Job: `JobAddRq`, `JobModRq`, `JobDelRq`, `JobQueryRq`, `JobListQueryRq`
- Sales Order: `SalesOrderAddRq`, `SalesOrderModRq`, `SalesOrderDelRq`, `SalesOrderQueryRq`, `SalesOrderListQueryRq`
- Requirement link: `ReqSatisfierAssign` with `SatisfierType` including `"PO"`

---

## COM + XML Flow (Conceptual)

1. Create COM object: `JBRequestProcessor`
2. `CreateSession(user, password) -> SessionID`
3. `ProcessRequest(xmlRequestString) -> xmlResponseString`
4. `CloseSession(SessionID)`

XML envelope:
- Root: `<JBXML>`
- Request: `<JBXMLRequest> ... </JBXMLRequest>`
- Response: `<JBXMLRespond> ... </JBXMLRespond>`

---

## PO Automation Pattern in Legacy JobBOSS

| Step | What to do via XML SDK                         | Why it matters for POs                         |
|------|-----------------------------------------------|-----------------------------------------------|
| 1    | Ensure Vendor exists (`VendorAddRq/ModRq`)    | Matches PO vendor header                      |
| 2    | Define Material (`MaterialAddRq` + vendor refs)| Matches PO line item (part, price, UOM)       |
| 3    | Create Jobs (`JobAddRq`)                      | Jobs like `25-027`…`25-036` from sample PO    |
| 4    | Add material requirements to jobs             | Represents demand for that purchased material |
| 5    | Use `ReqSatisfierAssign` with `SatisfierType="PO"` | Mark demand as to be satisfied by purchasing |
| 6    | Run JobBOSS purchasing/MRP                    | JobBOSS generates PO headers/lines            |

Notes and terms (QC text, “no China material”, etc.) are put into note/comment/user‑defined fields on materials, jobs, or standard texts, which purchasing uses when printing POs.

---

## Integration Strategy Guidance

- Prefer: XML SDK + JobBOSS purchasing (no direct PO inserts).
- Use direct SQL **read‑only** for reporting/triggers if needed.
- Avoid direct SQL **writes** to PO tables unless you fully accept schema/upgrade risk.

```

