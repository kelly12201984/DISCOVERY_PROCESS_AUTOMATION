"""
Extract physical tank specifications from available data sources.
No Compress XML in repo — we mine BOM (material_reqs), job descriptions, and price.

For each job, extracts:
  - material_grade: dominant steel grade (304L, 316L, SA36, 2205, etc.)
  - max_plate_thickness: thickest plate in BOM (inches)
  - plate_count: number of distinct plate entries
  - nozzle_count: number of pipe/flange entries (proxy for nozzle complexity)
  - flange_count: flanges in BOM
  - max_flange_size: largest flange diameter (inches)
  - head_count: number of head entries in BOM
  - has_code_stamp: ASME code stamp inferred from XRAY/RT entries + materials
  - capacity_gal: gallons parsed from description or BOM
  - total_material_cost: sum of estimated material costs
  - total_price: job price (scope proxy)
  - customer: repeat-customer pattern
  - tank_type: classified from description
  - is_batch: part of a multi-unit order (e.g., "3 OF 10")
  - batch_size: how many in the batch
"""
import re
import pandas as pd
import numpy as np
from config import JOBS_CSV, CLEAN_JOBS, DATA_DIR

JOBBOSS_DIR = DATA_DIR.parent.parent / "JOBBOSS_DATA"
MATERIAL_REQS = JOBBOSS_DIR / "material_reqs.csv"


# --- Material grade detection ---

GRADE_PRIORITY = [
    ("hastelloy", "HASTELLOY"),
    ("inconel", "INCONEL"),
    ("904l", "904L"),
    ("2205", "2205"),
    ("duplex", "DUPLEX"),
    ("316l", "316L"),
    ("316", "316"),
    ("304l", "304L"),
    ("304", "304"),
    ("sa240", "SA240"),
    ("sa516", "SA516"),
    ("sa36", "SA36"),
    ("a36", "A36"),
    ("cs", "CS"),
]


def detect_material_grade(descriptions: list[str]) -> str:
    combined = " ".join(str(d).upper() for d in descriptions if pd.notna(d))
    for pattern, label in GRADE_PRIORITY:
        if pattern.upper() in combined:
            return label
    return "UNKNOWN"


# --- Plate thickness extraction ---

PLATE_THICK_RE = re.compile(
    r'(?:PLATE|PLT)\s+\S+\s+(\d+(?:/\d+)?)"?\s*(?:X|x)',
    re.IGNORECASE
)

def parse_fraction(s: str) -> float:
    if "/" in s:
        parts = s.split("/")
        return float(parts[0]) / float(parts[1])
    return float(s)


def extract_plate_thickness(descriptions: list[str]) -> tuple[float, int]:
    """Return (max_thickness_inches, plate_count)."""
    thicknesses = []
    plate_count = 0
    for d in descriptions:
        if not isinstance(d, str):
            continue
        d_upper = d.upper()
        if "PLATE" not in d_upper and "PLT" not in d_upper:
            continue
        if "NAMEPLATE" in d_upper or "PLATED" in d_upper or "TEMPLATE" in d_upper:
            continue
        plate_count += 1
        m = PLATE_THICK_RE.search(d)
        if m:
            try:
                thicknesses.append(parse_fraction(m.group(1)))
            except (ValueError, ZeroDivisionError):
                pass
    return (max(thicknesses) if thicknesses else 0.0, plate_count)


# --- Nozzle/flange counting ---

FLANGE_SIZE_RE = re.compile(r'(\d+(?:\.\d+)?)"?\s*(?:\d+#|150|300|600|900|1500)', re.IGNORECASE)

def count_nozzles_flanges(descriptions: list[str]) -> dict:
    pipe_count = 0
    flange_count = 0
    max_flange_size = 0.0
    head_count = 0

    for d in descriptions:
        if not isinstance(d, str):
            continue
        d_upper = d.upper()

        if d_upper.startswith("PIPE ") or "PIPE " in d_upper:
            pipe_count += 1

        if "FLANGE" in d_upper:
            flange_count += 1
            m = FLANGE_SIZE_RE.search(d)
            if m:
                try:
                    size = float(m.group(1))
                    max_flange_size = max(max_flange_size, size)
                except ValueError:
                    pass

        if ("HEAD" in d_upper or "ASME 2:1" in d_upper or "DISH" in d_upper or "ELLIP" in d_upper):
            if "HEX" not in d_upper and "PLUG" not in d_upper:
                head_count += 1

    return {
        "nozzle_count": pipe_count,
        "flange_count": flange_count,
        "max_flange_size": max_flange_size,
        "head_count": head_count,
    }


# --- Code stamp detection ---

def detect_code_stamp(descriptions: list[str]) -> bool:
    combined = " ".join(str(d).upper() for d in descriptions if pd.notna(d))
    indicators = ["XRAY", "X-RAY", "SPOT XRAY", "RT ", "RADIOGRAPH",
                   "ASME", "CODE STAMP", "PWHT", "HYDRO TEST",
                   "DYE PEN", "UT EXAM"]
    return any(ind in combined for ind in indicators)


# --- Description parsing ---

CAPACITY_RE = re.compile(r'(\d[\d,]*)\s*(?:GAL|GALLON)', re.IGNORECASE)
BATCH_RE = re.compile(r'(\d+)\s*(?:OF|of)\s*(\d+)', re.IGNORECASE)

TANK_PATTERNS = {
    "storage_tank":    r"storage\s+tank|bulk\s+storage",
    "buffer_tank":     r"buffer\s+tank",
    "dissolving_tank": r"dissolving|smelt",
    "reactor":         r"reactor|cstr|packed\s+bed",
    "separator":       r"separator|stripper",
    "surge_tank":      r"surge\s+tank|surge\s+drum",
    "flash_tank":      r"flash\s+tank",
    "crystallizer":    r"crystal[li]zer",
    "dryer_plate":     r"dryer\s+plate",
    "handrail_ladder": r"handrail|ladder",
    "heat_exchanger":  r"exchanger|heater|cooler",
    "vessel":          r"vessel|pressure",
    "tank":            r"tank",
}

def parse_description(desc: str) -> dict:
    if not isinstance(desc, str):
        return {"capacity_gal": 0, "tank_type": "unknown", "is_batch": False, "batch_size": 1}

    # Capacity
    cap_match = CAPACITY_RE.search(desc)
    capacity = int(cap_match.group(1).replace(",", "")) if cap_match else 0

    # Batch detection
    batch_match = BATCH_RE.search(desc)
    is_batch = batch_match is not None
    batch_size = int(batch_match.group(2)) if batch_match else 1

    # Tank type
    desc_lower = desc.lower()
    tank_type = "other"
    for ttype, pattern in TANK_PATTERNS.items():
        if re.search(pattern, desc_lower):
            tank_type = ttype
            break

    return {
        "capacity_gal": capacity,
        "tank_type": tank_type,
        "is_batch": is_batch,
        "batch_size": batch_size,
    }


# --- Plate dimension parsing from Material column ---

PLATE_DIM_RE = re.compile(
    r'(\d+/\d+|\d+\.\d+|\d+)\s*"?\s*[Xx]\s*(\d+(?:\.\d+)?)\s*"?\s*(?:[Xx]\s*(\d+(?:\.\d+)?))?',
    re.IGNORECASE
)


def parse_plate_dimensions(bom: pd.DataFrame) -> dict:
    """Extract plate quantities, widths, and thicknesses from BOM."""
    plates = bom[bom["Material"].fillna("").str.upper().str.contains(r"\bPLT\b|\bPLATE\b", regex=True)]
    plates = plates[~plates["Material"].fillna("").str.upper().str.contains("NAMEPLATE|PLATED|TEMPLATE")]

    if plates.empty:
        return {
            "total_plate_qty": 0, "total_plate_cost": 0, "n_plate_lines": 0,
            "max_plate_width": 0, "avg_plate_thickness": 0, "n_distinct_thicknesses": 0,
        }

    total_qty = plates["Est_Qty"].fillna(0).sum()
    total_cost = plates["Est_Total_Cost"].fillna(0).sum()

    widths = []
    thicknesses = []
    for _, r in plates.iterrows():
        mat = str(r.get("Material", "")).upper()
        m = PLATE_DIM_RE.search(mat)
        if not m:
            continue
        try:
            t_str = m.group(1)
            thickness = parse_fraction(t_str)
            thicknesses.append(thickness)
        except (ValueError, ZeroDivisionError):
            pass
        if m.group(2):
            try:
                widths.append(float(m.group(2)))
            except ValueError:
                pass

    return {
        "total_plate_qty": total_qty,
        "total_plate_cost": total_cost,
        "n_plate_lines": len(plates),
        "max_plate_width": max(widths) if widths else 0,
        "avg_plate_thickness": sum(thicknesses) / len(thicknesses) if thicknesses else 0,
        "n_distinct_thicknesses": len(set(round(t, 4) for t in thicknesses)),
    }


# --- Main spec extraction ---

def extract_all_specs() -> pd.DataFrame:
    """Build tank_specs table from BOM + jobs data."""
    jobs = pd.read_csv(CLEAN_JOBS)
    mr = pd.read_csv(MATERIAL_REQS)

    # Filter material_reqs to jobs in our cleaned set
    valid_jobs = set(jobs["Job"])
    mr = mr[mr["Job"].isin(valid_jobs)]

    rows = []
    for _, job in jobs.iterrows():
        job_no = job["Job"]

        # Get BOM for this job
        bom = mr[mr["Job"] == job_no]
        bom_descs = bom["Description"].tolist() + bom["Material"].tolist()

        # Material grade
        material_grade = detect_material_grade(bom_descs)

        # Plate thickness
        max_thick, plate_count = extract_plate_thickness(bom_descs)

        # Nozzle/flange/head counts
        nf = count_nozzles_flanges(bom_descs)

        # Code stamp
        has_code = detect_code_stamp(bom_descs)

        # Material cost
        mat_cost = bom["Est_Total_Cost"].sum() if len(bom) > 0 else 0

        # Plate dimensions (steel volume proxy)
        plate_dims = parse_plate_dimensions(bom)

        # Description parsing
        desc_info = parse_description(job.get("Description"))

        # Certs required count (proxy for code complexity)
        certs = bom["Certs_Required"].fillna("").astype(str)
        certs_count = (certs.str.upper() == "TRUE").sum() + (certs == "1").sum()

        rows.append({
            "Job": job_no,
            "Customer": job.get("Customer", ""),
            "Description": job.get("Description", ""),
            "Status": job.get("Status", ""),
            "Order_Date": job.get("Order_Date", ""),
            "Est_Total_Hrs": job.get("Est_Total_Hrs", 0),
            "Act_Total_Hrs": job.get("Act_Total_Hrs", 0),
            "Total_Price": job.get("Total_Price", 0),
            # Spec features
            "material_grade": material_grade,
            "max_plate_thickness": max_thick,
            "plate_count": plate_count,
            "nozzle_count": nf["nozzle_count"],
            "flange_count": nf["flange_count"],
            "max_flange_size": nf["max_flange_size"],
            "head_count": nf["head_count"],
            "has_code_stamp": has_code,
            "total_material_cost": mat_cost,
            "certs_required_count": certs_count,
            # Plate dimensions (shell/steel volume proxy)
            "total_plate_qty": plate_dims["total_plate_qty"],
            "total_plate_cost": plate_dims["total_plate_cost"],
            "n_plate_lines": plate_dims["n_plate_lines"],
            "max_plate_width": plate_dims["max_plate_width"],
            "avg_plate_thickness": plate_dims["avg_plate_thickness"],
            "n_distinct_thicknesses": plate_dims["n_distinct_thicknesses"],
            # Description-derived
            "capacity_gal": desc_info["capacity_gal"],
            "tank_type": desc_info["tank_type"],
            "is_batch": desc_info["is_batch"],
            "batch_size": desc_info["batch_size"],
        })

    return pd.DataFrame(rows)


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    print("Extracting tank specs from BOM + descriptions + price...")
    specs = extract_all_specs()

    print(f"\n{len(specs)} jobs with specs extracted")
    print(f"\nMaterial grade distribution:")
    print(specs["material_grade"].value_counts().to_string())
    print(f"\nTank type distribution:")
    print(specs["tank_type"].value_counts().to_string())
    print(f"\nSpec coverage:")
    print(f"  Jobs with plate data:      {(specs['plate_count'] > 0).sum()}")
    print(f"  Jobs with nozzle data:     {(specs['nozzle_count'] > 0).sum()}")
    print(f"  Jobs with flange data:     {(specs['flange_count'] > 0).sum()}")
    print(f"  Jobs with head data:       {(specs['head_count'] > 0).sum()}")
    print(f"  Jobs with code stamp:      {specs['has_code_stamp'].sum()}")
    print(f"  Jobs with capacity:        {(specs['capacity_gal'] > 0).sum()}")
    print(f"  Jobs with price:           {(specs['Total_Price'] > 0).sum()}")
    print(f"  Jobs with material cost:   {(specs['total_material_cost'] > 0).sum()}")

    print(f"\nMax plate thickness stats:")
    thick = specs[specs["max_plate_thickness"] > 0]["max_plate_thickness"]
    if len(thick) > 0:
        print(f"  Range: {thick.min():.3f}\" - {thick.max():.3f}\"")
        print(f"  Median: {thick.median():.3f}\"")

    out = DATA_DIR / "tank_specs.csv"
    specs.to_csv(out, index=False)
    print(f"\nSaved: {out}")


if __name__ == "__main__":
    main()
