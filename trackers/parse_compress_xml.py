"""
COMPRESS XML Parser — extracts structured vessel data from Codeware COMPRESS exports.

Reads .xml / .xml3d files exported from COMPRESS and produces:
  1. Vessel summary (design conditions, dimensions, weights, capacity)
  2. QC data sheet (hydro test pressure, MDMT, RT requirements, PWHT, materials)
  3. Bill of Materials (every component with material spec, dimensions, weight)
  4. Nozzle schedule (size, type, rating, orientation, weld sizes)

Usage:
    python parse_compress_xml.py <path_to_xml>           # print summary
    python parse_compress_xml.py <path_to_xml> --excel    # export to Excel
    python parse_compress_xml.py --all                    # parse all XMLs in Drawings/
"""
import xml.etree.ElementTree as ET
import sys
import os
import json

DRAWINGS_DIR = os.path.join(os.path.dirname(__file__), '..', 'Drawings')
OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'generated_trackers')

NS = {'cw': 'urn:PressureVessel'}


def parse_vessel(xml_path):
    """Parse a COMPRESS XML file and return structured vessel data."""
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Navigate to pressureVessel element
    pv = root.find('.//pressureVessel') or root.find('.//cw:pressureVessel', NS)
    if pv is None:
        # Try without namespace
        pv = root.find('pressureVessel')
    if pv is None:
        raise ValueError(f"No pressureVessel element found in {xml_path}")

    vessel = {
        'file': os.path.basename(xml_path),
        'general': parse_general_info(pv),
        'design_conditions': parse_design_conditions(pv),
        'weights': parse_weights(pv),
        'components': parse_components(pv),
        'nozzles': parse_nozzles(pv),
        'revisions': parse_revisions(pv),
    }
    return vessel


def get_text(element, tag, default=''):
    """Get text content of a child element, searching with and without namespace."""
    if element is None:
        return default
    el = element.find(tag)
    if el is None:
        el = element.find(f'cw:{tag}', NS)
    if el is not None and el.text:
        return el.text.strip()
    return default


def get_float(element, tag, default=0.0):
    """Get float value from child element."""
    val = get_text(element, tag, '')
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def get_units(element, tag):
    """Get value and units from an element with units attribute."""
    if element is None:
        return '', ''
    el = element.find(tag)
    if el is None:
        el = element.find(f'cw:{tag}', NS)
    if el is not None:
        val = el.text.strip() if el.text else ''
        units = el.get('units', '')
        return val, units
    return '', ''


def parse_general_info(pv):
    """Extract general vessel info."""
    gi = pv.find('.//generalVesselInfo')
    if gi is None:
        return {}
    return {
        'identifier': get_text(gi, 'identifier'),
        'designCode': get_text(gi, 'designCode'),
        'designCodeEdition': get_text(gi, 'designCodeEdition'),
        'units': get_text(gi, 'units'),
        'orientation': get_text(gi, 'orientation'),
        'tangentToTangentLength': get_float(gi, 'tangentToTangentLength'),
        'structureHeight': get_float(gi, 'structureHeight'),
        'outerDiameter': get_float(gi, 'outerDiameter'),
        'purchaseOrderNumber': get_text(gi, 'purchaseOrderNumber'),
    }


def parse_design_conditions(pv):
    """Extract pressure chamber design conditions."""
    pc = pv.find('.//pressureChamberConditions')
    if pc is None:
        return {}

    # Materials sub-element
    mats = pc.find('materials')
    materials = {}
    if mats is not None:
        for child in mats:
            materials[child.tag] = child.text.strip() if child.text else ''

    return {
        'chamber': get_text(pc, 'identifier'),
        'designPressure': get_float(pc, 'designPressure'),
        'designTemperature': get_float(pc, 'designTemperature'),
        'MAWP': get_float(pc, 'MAWP'),
        'MAWPTemperature': get_float(pc, 'MAWPTemperature'),
        'MAP': get_float(pc, 'MAP'),
        'MAPTemperature': get_float(pc, 'MAPTemperature'),
        'MAEP': get_float(pc, 'MAEP'),
        'externalPressure': get_float(pc, 'externalPressure'),
        'externalTemperature': get_float(pc, 'externalTemperature'),
        'hydrostaticTestPressure': get_float(pc, 'hydrostaticTestPressure'),
        'MDMT': get_float(pc, 'MDMT'),
        'designMDMT': get_float(pc, 'designMDMT'),
        'lethalService': get_text(pc, 'lethalService'),
        'RT': get_text(pc, 'RT'),
        'PWHT': get_text(pc, 'PWHT'),
        'innerCorrosion': get_float(pc, 'innerCorrosion'),
        'outerCorrosion': get_float(pc, 'outerCorrosion'),
        'materials': materials,
    }


def parse_weights(pv):
    """Extract vessel weight and capacity results."""
    vr = pv.find('.//vesselResults')
    if vr is None:
        return {}
    return {
        'weightOperatingNew': get_float(vr, 'weightOperatingNew'),
        'weightOperatingCorroded': get_float(vr, 'weightOperatingCorroded'),
        'weightEmptyNew': get_float(vr, 'weightEmptyNew'),
        'weightEmptyCorroded': get_float(vr, 'weightEmptyCorroded'),
        'weightTestNew': get_float(vr, 'weightTestNew'),
        'capacityNew': get_float(vr, 'capacityNew'),
        'capacityCorroded': get_float(vr, 'capacityCorroded'),
        'liquidWeightOperating': get_float(vr, 'liquidWeightOperating'),
        'weightLift': get_float(vr, 'weightLift'),
    }


def parse_component(scd):
    """Parse a standardComponentData element into a dict."""
    comp = {
        'identifier': get_text(scd, 'identifier'),
        'material': get_text(scd, 'material'),
        'attachedTo': get_text(scd, 'attachedTo'),
        'nominalThickness': get_float(scd, 'nominalThickness'),
        'designThickness': get_float(scd, 'designThickness'),
        'requiredThickness': get_float(scd, 'requiredThickness'),
        'innerDiameter': get_float(scd, 'innerDiameter'),
        'outerDiameter': get_float(scd, 'outerDiameter'),
        'length': get_float(scd, 'length'),
        'weightNew': get_float(scd, 'weightNew'),
        'capacityNew': get_float(scd, 'capacityNew'),
        'startElevation': get_float(scd, 'startElevation'),
        'endElevation': get_float(scd, 'endElevation'),
        'staticHeadOperating': get_float(scd, 'staticHeadOperating'),
    }

    # Radiography
    rt_long = scd.find('.//radiographyLongSeam')
    rt_circ = scd.find('.//radiographyCircSeam')
    comp['rtLongSeam'] = rt_long.text.strip() if rt_long is not None and rt_long.text else ''
    comp['rtCircSeam'] = rt_circ.text.strip() if rt_circ is not None and rt_circ.text else ''

    # PWHT
    pwht = scd.find('.//postWeldHeatTreatment')
    comp['pwht'] = pwht.text.strip() if pwht is not None and pwht.text else ''

    # Crown/knuckle for heads
    comp['crownRadius'] = get_float(scd, 'crownRadius')
    comp['knuckleRadius'] = get_float(scd, 'knuckleRadius')

    return comp


def parse_components(pv):
    """Walk the full tree and extract all shell/head/closure components."""
    components = []

    # Find all standardComponentData elements anywhere in the tree
    for scd in pv.iter('standardComponentData'):
        comp = parse_component(scd)
        if comp['identifier']:
            components.append(comp)

    return components


def parse_nozzle_data(nozzle_el):
    """Parse a nozzle element (wrapper around standardComponentData + extras)."""
    scd = nozzle_el.find('.//standardComponentData')
    if scd is None:
        return None

    nzl = parse_component(scd)

    # Nozzle-specific fields
    nzl['nozzleType'] = get_text(scd, 'nozzleType') or get_text(nozzle_el, 'nozzleType')
    nzl['nozzleStyle'] = get_text(scd, 'nozzleStyle') or get_text(nozzle_el, 'nozzleStyle')
    nzl['fittingType'] = get_text(scd, 'fittingType')
    nzl['fittingEndStyle'] = get_text(scd, 'fittingEndStyle')
    nzl['drawingMark'] = get_text(scd, 'drawingMark')

    # Orientation
    nzl['orientationAngle'] = get_float(scd, 'orientationAngle')
    nzl['orientationType'] = get_text(scd, 'orientationType')
    nzl['minimumInternalProjection'] = get_float(scd, 'minimumInternalProjection')

    # Weld data
    wd = scd.find('.//weldData') or nozzle_el.find('.//weldData')
    if wd is not None:
        nzl['innerFilletWeld'] = get_float(wd, 'innerFilletWeld')
        nzl['outerFilletWeld'] = get_float(wd, 'outerFilletWeld')
        nzl['lowerGrooveWeld'] = get_float(wd, 'lowerGrooveWeld')
        nzl['upperGrooveWeld'] = get_float(wd, 'upperGrooveWeld')

    # Reinforcing pad
    pad = scd.find('.//reinforcingPad') or nozzle_el.find('.//reinforcingPad')
    if pad is not None:
        has_pad = get_text(pad, 'hasPad')
        if has_pad == 'TRUE':
            nzl['padMaterial'] = get_text(pad, 'material')
            nzl['padThickness'] = get_float(pad, 'nominalThickness')
            nzl['padWidth'] = get_float(pad, 'width')

    # Flange
    flange = scd.find('.//attachedFlange') or nozzle_el.find('.//attachedFlange')
    if flange is not None:
        nzl['flangeCode'] = get_text(flange, 'flangeCode')
        nzl['flangeType'] = get_text(flange, 'flangeType')
        nzl['flangeClass'] = get_text(flange, 'flangeClass')
        nzl['flangeSize'] = get_float(flange, 'nominalSize')
        nzl['boltCount'] = get_float(flange, 'numberOfBolts')
        nzl['boltDiameter'] = get_float(flange, 'boltDiameter')
        nzl['boltMaterial'] = get_text(flange, 'boltMaterial')

    return nzl


def parse_nozzles(pv):
    """Find all nozzle elements in the vessel tree."""
    nozzles = []

    # Nozzles can be nested in various locations — search broadly
    for tag in ['nozzle', 'couplingNozzle', 'flangedNozzle', 'weldNeckNozzle']:
        for nzl_el in pv.iter(tag):
            nzl = parse_nozzle_data(nzl_el)
            if nzl and nzl['identifier']:
                nozzles.append(nzl)

    # De-duplicate (components already found nozzle SCDs)
    seen = set()
    unique = []
    for n in nozzles:
        if n['identifier'] not in seen:
            seen.add(n['identifier'])
            unique.append(n)

    return unique


def parse_revisions(pv):
    """Extract revision history."""
    revisions = []
    for rev in pv.iter('revision'):
        revisions.append({
            'revNumber': get_text(rev, 'revNumber'),
            'revDate': get_text(rev, 'revDate'),
            'operator': get_text(rev, 'operator'),
            'notes': get_text(rev, 'notes'),
        })
    return revisions


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------

def print_summary(vessel):
    """Print a human-readable vessel summary."""
    g = vessel['general']
    d = vessel['design_conditions']
    w = vessel['weights']

    print('=' * 70)
    print(f"VESSEL: {g.get('identifier', 'Unknown')}")
    print(f"File:   {vessel['file']}")
    print('=' * 70)

    print(f"\n--- GENERAL ---")
    print(f"  Design Code:    {g.get('designCode', '')} ({g.get('designCodeEdition', '')})")
    print(f"  Orientation:    {g.get('orientation', '')}")
    print(f"  OD:             {g.get('outerDiameter', 0):.2f} in")
    print(f"  T-T Length:     {g.get('tangentToTangentLength', 0):.2f} in")
    print(f"  Height:         {g.get('structureHeight', 0):.2f} in")

    print(f"\n--- DESIGN CONDITIONS ---")
    print(f"  Design Pressure:  {d.get('designPressure', 0):.1f} psi")
    print(f"  Design Temp:      {d.get('designTemperature', 0):.0f} °F")
    print(f"  MAWP:             {d.get('MAWP', 0):.1f} psi @ {d.get('MAWPTemperature', 0):.0f} °F")
    print(f"  MAP:              {d.get('MAP', 0):.1f} psi @ {d.get('MAPTemperature', 0):.0f} °F")
    print(f"  Hydro Test:       {d.get('hydrostaticTestPressure', 0):.1f} psi")
    print(f"  MDMT:             {d.get('MDMT', 0):.0f} °F (design: {d.get('designMDMT', 0):.0f} °F)")
    print(f"  Ext Pressure:     {d.get('externalPressure', 0):.1f} psi")
    print(f"  Lethal Service:   {d.get('lethalService', '')}")
    print(f"  RT:               {d.get('RT', '')}")
    print(f"  PWHT:             {d.get('PWHT', '')}")
    print(f"  Corrosion:        {d.get('innerCorrosion', 0):.4f} in (inner) / {d.get('outerCorrosion', 0):.4f} in (outer)")

    mats = d.get('materials', {})
    if mats:
        print(f"\n--- PRIMARY MATERIALS ---")
        for comp_type, spec in mats.items():
            print(f"  {comp_type:15s}  {spec}")

    print(f"\n--- WEIGHTS & CAPACITY ---")
    print(f"  Empty (new):      {w.get('weightEmptyNew', 0):,.1f} lbf")
    print(f"  Operating (new):  {w.get('weightOperatingNew', 0):,.1f} lbf")
    print(f"  Test (new):       {w.get('weightTestNew', 0):,.1f} lbf")
    print(f"  Lift:             {w.get('weightLift', 0):,.1f} lbf")
    print(f"  Capacity (new):   {w.get('capacityNew', 0):,.1f} US gal")

    comps = vessel['components']
    if comps:
        print(f"\n--- COMPONENTS ({len(comps)}) ---")
        print(f"  {'Identifier':30s} {'Material':15s} {'Thk (in)':>10s} {'Wt (lbf)':>10s} {'RT Long':>20s}")
        print(f"  {'-'*30} {'-'*15} {'-'*10} {'-'*10} {'-'*20}")
        for c in comps:
            ident = c.get('identifier', '')[:30]
            # Skip nozzle components here — they show up in nozzle schedule
            if 'Nozzle' in ident or 'nozzle' in ident:
                continue
            print(f"  {ident:30s} {c.get('material',''):15s} {c.get('nominalThickness',0):>10.4f} {c.get('weightNew',0):>10.1f} {c.get('rtLongSeam',''):>20s}")

    nozzles = vessel['nozzles']
    if nozzles:
        print(f"\n--- NOZZLE SCHEDULE ({len(nozzles)}) ---")
        print(f"  {'Mark':6s} {'Identifier':25s} {'Material':15s} {'ID (in)':>8s} {'OD (in)':>8s} {'Flange':>12s} {'Orient':>8s}")
        print(f"  {'-'*6} {'-'*25} {'-'*15} {'-'*8} {'-'*8} {'-'*12} {'-'*8}")
        for n in nozzles:
            mark = n.get('drawingMark', '')
            ident = n.get('identifier', '')[:25]
            mat = n.get('material', '')[:15]
            iid = n.get('innerDiameter', 0)
            oid = n.get('outerDiameter', 0)
            flg = ''
            if n.get('flangeClass'):
                flg = f"{n.get('flangeSize',0):.0f}\" {n.get('flangeClass','')}"
            orient = f"{n.get('orientationAngle', 0):.0f}°"
            print(f"  {mark:6s} {ident:25s} {mat:15s} {iid:>8.3f} {oid:>8.3f} {flg:>12s} {orient:>8s}")

    revs = vessel['revisions']
    if revs:
        print(f"\n--- REVISIONS ---")
        for r in revs:
            print(f"  Rev {r['revNumber']}: {r['revDate']} by {r['operator']} — {r['notes'][:60]}")

    print()


def export_qc_sheet(vessel):
    """Return a dict of QC-relevant data for a vessel."""
    g = vessel['general']
    d = vessel['design_conditions']
    w = vessel['weights']
    mats = d.get('materials', {})

    qc = {
        'Vessel ID': g.get('identifier', ''),
        'Design Code': f"{g.get('designCode', '')} {g.get('designCodeEdition', '')}",
        'Design Pressure (psi)': d.get('designPressure', 0),
        'Design Temperature (°F)': d.get('designTemperature', 0),
        'MAWP (psi)': d.get('MAWP', 0),
        'MAWP Temperature (°F)': d.get('MAWPTemperature', 0),
        'Hydro Test Pressure (psi)': d.get('hydrostaticTestPressure', 0),
        'MDMT (°F)': d.get('MDMT', 0),
        'Design MDMT (°F)': d.get('designMDMT', 0),
        'Lethal Service': d.get('lethalService', ''),
        'RT Requirement': d.get('RT', ''),
        'PWHT': d.get('PWHT', ''),
        'Inner Corrosion Allowance (in)': d.get('innerCorrosion', 0),
        'Shell Material': mats.get('cylinders', ''),
        'Head Material': mats.get('heads', ''),
        'Support Material': mats.get('support', ''),
        'Weight Empty (lbf)': w.get('weightEmptyNew', 0),
        'Weight Operating (lbf)': w.get('weightOperatingNew', 0),
        'Weight Test (lbf)': w.get('weightTestNew', 0),
        'Capacity (gal)': w.get('capacityNew', 0),
    }
    return qc


def export_bom(vessel):
    """Return a list of BOM line items from components + nozzles."""
    bom = []
    for c in vessel['components']:
        ident = c.get('identifier', '')
        if 'Nozzle' in ident or 'nozzle' in ident:
            continue
        bom.append({
            'Component': ident,
            'Material Spec': c.get('material', ''),
            'Nominal Thk (in)': c.get('nominalThickness', 0),
            'ID (in)': c.get('innerDiameter', 0),
            'OD (in)': c.get('outerDiameter', 0),
            'Length (in)': c.get('length', 0),
            'Weight (lbf)': c.get('weightNew', 0),
        })

    for n in vessel['nozzles']:
        flange_desc = ''
        if n.get('flangeClass'):
            flange_desc = f"{n.get('flangeSize',0):.0f}\" {n.get('flangeClass','')} {n.get('flangeType','')}"
        bom.append({
            'Component': f"Nozzle {n.get('drawingMark', '')} — {n.get('identifier', '')}",
            'Material Spec': n.get('material', ''),
            'Nominal Thk (in)': n.get('nominalThickness', 0),
            'ID (in)': n.get('innerDiameter', 0),
            'OD (in)': n.get('outerDiameter', 0),
            'Length (in)': 0,
            'Weight (lbf)': n.get('weightNew', 0),
            'Flange': flange_desc,
        })

    return bom


def export_to_excel(vessel, outfile):
    """Export vessel data to a multi-sheet Excel file."""
    import pandas as pd

    with pd.ExcelWriter(outfile, engine='openpyxl') as writer:
        # QC Sheet
        qc = export_qc_sheet(vessel)
        qc_df = pd.DataFrame([qc]).T
        qc_df.columns = ['Value']
        qc_df.index.name = 'Parameter'
        qc_df.to_excel(writer, sheet_name='QC Data')

        # BOM
        bom = export_bom(vessel)
        if bom:
            bom_df = pd.DataFrame(bom)
            bom_df.to_excel(writer, sheet_name='BOM', index=False)

        # Nozzle Schedule
        nozzles = vessel['nozzles']
        if nozzles:
            nzl_rows = []
            for n in nozzles:
                nzl_rows.append({
                    'Mark': n.get('drawingMark', ''),
                    'Identifier': n.get('identifier', ''),
                    'Attached To': n.get('attachedTo', ''),
                    'Material': n.get('material', ''),
                    'ID (in)': n.get('innerDiameter', 0),
                    'OD (in)': n.get('outerDiameter', 0),
                    'Thk (in)': n.get('nominalThickness', 0),
                    'Orientation (°)': n.get('orientationAngle', 0),
                    'Elevation (in)': n.get('startElevation', 0),
                    'RT Long Seam': n.get('rtLongSeam', ''),
                    'Flange Class': n.get('flangeClass', ''),
                    'Flange Size': n.get('flangeSize', ''),
                    'Bolt Count': n.get('boltCount', ''),
                    'Bolt Dia': n.get('boltDiameter', ''),
                    'Inner Fillet Weld': n.get('innerFilletWeld', ''),
                    'Lower Groove Weld': n.get('lowerGrooveWeld', ''),
                    'Pad Material': n.get('padMaterial', ''),
                    'Pad Thk': n.get('padThickness', ''),
                })
            nzl_df = pd.DataFrame(nzl_rows)
            nzl_df.to_excel(writer, sheet_name='Nozzle Schedule', index=False)

        # Components
        comps = vessel['components']
        if comps:
            comp_rows = []
            for c in comps:
                if 'Nozzle' in c.get('identifier', ''):
                    continue
                comp_rows.append({
                    'Component': c.get('identifier', ''),
                    'Material': c.get('material', ''),
                    'Attached To': c.get('attachedTo', ''),
                    'Nom Thk (in)': c.get('nominalThickness', 0),
                    'Reqd Thk (in)': c.get('requiredThickness', 0),
                    'ID (in)': c.get('innerDiameter', 0),
                    'OD (in)': c.get('outerDiameter', 0),
                    'Length (in)': c.get('length', 0),
                    'Weight (lbf)': c.get('weightNew', 0),
                    'Capacity (gal)': c.get('capacityNew', 0),
                    'RT Long Seam': c.get('rtLongSeam', ''),
                    'RT Circ Seam': c.get('rtCircSeam', ''),
                    'PWHT': c.get('pwht', ''),
                })
            if comp_rows:
                comp_df = pd.DataFrame(comp_rows)
                comp_df.to_excel(writer, sheet_name='Components', index=False)

    print(f"Exported: {outfile}")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    if len(sys.argv) < 2:
        print(__doc__)
        return

    excel_mode = '--excel' in sys.argv
    all_mode = '--all' in sys.argv

    if all_mode:
        xml_files = []
        for f in os.listdir(DRAWINGS_DIR):
            if f.endswith('.xml') or f.endswith('.xml3d'):
                xml_files.append(os.path.join(DRAWINGS_DIR, f))
    else:
        xml_files = [a for a in sys.argv[1:] if not a.startswith('--')]

    for xml_path in xml_files:
        try:
            vessel = parse_vessel(xml_path)
            print_summary(vessel)

            if excel_mode:
                base = os.path.splitext(os.path.basename(xml_path))[0]
                outfile = os.path.join(OUT_DIR, f'Vessel_{base}.xlsx')
                export_to_excel(vessel, outfile)

        except Exception as e:
            print(f"ERROR parsing {xml_path}: {e}")
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    main()
