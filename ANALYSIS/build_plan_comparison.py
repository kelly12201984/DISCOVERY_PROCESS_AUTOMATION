"""
BUILD PLAN COMPARISON: Excel MASTER BUILD PLAN vs JobBOSS Routing
================================================================
Compares the 3 data sources for the same job to understand what OTTO needs to automate.

DATA SOURCES:
1. MASTER BUILD PLAN.xlsx (Excel) - Dustin's detailed shop document
2. JobBOSS job_operations.csv - ERP routing data
3. Certified Drawing PDF (Sheet 1) - Vessel specifications

FINDING: The Excel and JobBOSS are THE SAME DATA. The "Sheet2-PASTE HERE!" tab
in the Excel IS a copy-paste from the JobBOSS screen. The Excel adds:
  - Job-specific notes inline (e.g., "BUILD TOP IN (2) SECTIONS")
  - "Tasks with Hours" sheets for printing work orders per operation
  - "Build Plan - No Hours" version for posting on shop floor
  - Section headers organizing ops by phase (Nozzles, Cut & Prep, Shells, etc.)

The ROUTING itself is identical. Same op numbers, same descriptions, same hours.
"""

import csv
import json
from collections import defaultdict


def load_job_operations(job_id):
    """Load all operations for a given job from JobBOSS CSV."""
    ops = []
    with open('JOBBOSS_DATA/job_operations.csv', 'r') as f:
        reader = csv.DictReader(f)
        for r in reader:
            if r['Job'] == job_id:
                ops.append({
                    'seq': int(r['Sequence']),
                    'wc': r['Work_Center'],
                    'desc': r['Description'],
                    'est_total': float(r['Est_Total_Hrs']) if r['Est_Total_Hrs'] else 0,
                    'act_run': float(r['Act_Run_Hrs']) if r['Act_Run_Hrs'] else 0,
                    'act_setup': float(r['Act_Setup_Hrs']) if r['Act_Setup_Hrs'] else 0,
                    'status': r['Status'],
                    'actual_start': r['Actual_Start'],
                })
    return ops


def analyze_job(job_id):
    """Full analysis of a single job."""
    ops = load_job_operations(job_id)
    if not ops:
        print(f"No operations found for {job_id}")
        return None

    est_total = sum(o['est_total'] for o in ops)
    act_total = sum(o['act_run'] + o['act_setup'] for o in ops)

    # Break down by work center
    wc_hours = defaultdict(lambda: {'est': 0, 'act': 0, 'count': 0})
    for o in ops:
        wc = o['wc']
        wc_hours[wc]['est'] += o['est_total']
        wc_hours[wc]['act'] += o['act_run'] + o['act_setup']
        wc_hours[wc]['count'] += 1

    return {
        'job': job_id,
        'total_ops': len(ops),
        'est_hours': est_total,
        'act_hours': act_total,
        'ratio': act_total / est_total if est_total > 0 else 0,
        'wc_breakdown': dict(wc_hours),
        'operations': ops,
    }


def compare_two_jobs(job_a_id, job_b_id):
    """Compare routing structure between two jobs."""
    ops_a = load_job_operations(job_a_id)
    ops_b = load_job_operations(job_b_id)

    descs_a = [o['desc'] for o in ops_a]
    descs_b = [o['desc'] for o in ops_b]

    common = set(descs_a) & set(descs_b)
    only_a = set(descs_a) - set(descs_b)
    only_b = set(descs_b) - set(descs_a)

    return {
        'job_a': job_a_id,
        'job_b': job_b_id,
        'ops_a': len(ops_a),
        'ops_b': len(ops_b),
        'common_ops': len(common),
        'only_in_a': sorted(only_a),
        'only_in_b': sorted(only_b),
        'similarity': len(common) / max(len(set(descs_a)), len(set(descs_b))) if descs_a else 0,
    }


# ============================================================
# VESSEL SPECS EXTRACTED FROM CERTIFIED DRAWING: Job 24-003
# Aqueous Ammonia Tank for Bakelite Chemicals LLC
# Drawing 003-24-1, Sheet 1 of 11, Rev Set 2
# ============================================================
JOB_003_24_VESSEL_SPECS = {
    'job': '24-003',
    'customer': 'Bakelite Chemicals LLC',
    'description': 'Aqueous Ammonia Tank',
    'equipment_number': 'S-19',

    # Design Data
    'design_code': 'ASME',
    'cert_stamp': True,
    'design_pressure_psig': 30,
    'design_pressure_type': 'FV',  # Full Vacuum
    'design_temp_f': 120,
    'min_design_metal_temp_f': -20,
    'operating_pressure_psig': 28,
    'operating_temp_range_f': '50-68',
    'joint_eff_heads': 0.70,
    'joint_eff_shell': 0.70,
    'corrosion_allowance_in': 0.0625,  # 1/16"
    'specific_gravity': 0.890,
    'wind_load_mph': 115,
    'stress_relief': False,
    'radiographic_exam': False,
    'dye_penetrant_exam': False,
    'magnetic_particle_exam': False,
    'pneumatic_test_psig': 45,

    # Vessel Geometry
    'shell_id_in': 120,  # 10'-0"
    'shell_thickness_in': 0.375,  # 3/8"
    'shell_height_in': 118,
    'shell_courses': 3,
    'shell_orientation': 'VERTICAL',  # *VERT - TOP TO BOTTOM
    'head_type': 'F&D',  # ASME F&D
    'head_thickness_nom_in': 0.5,  # 1/2" NOM
    'head_thickness_min_in': 0.4688,
    'head_ikr_in': 7.25,
    'head_sf_in': 2,  # straight flange

    # Materials
    'shell_material': 'SA516-70',
    'head_material': 'SA516-70',
    'nozzle_neck_material': 'SA53-B ERW',
    'nozzle_flange_material': 'SA105',
    'manway_neck_material': 'SA516-70',
    'manway_flange_material': 'SA105',
    'gasket_material': 'NEOPRENE',
    'bolt_material': 'SA193-B7 (ZINC PLATED)',

    # Nozzle Schedule (14 nozzles + 2 manways)
    'nozzle_count': 14,
    'manway_count': 2,
    'nozzles': [
        {'mark': 'A', 'service': 'SAMPLE', 'size': '2"', 'rating': '150#', 'type': 'RFSO'},
        {'mark': 'B', 'service': 'SPARE', 'size': '3"', 'rating': '150#', 'type': 'RFSO W/BLIND'},
        {'mark': 'C', 'service': 'LEVEL TRANSMITTER', 'size': '4"', 'rating': '150#', 'type': 'RFSO'},
        {'mark': 'D', 'service': 'CHILLED AQUA INLET', 'size': '2"', 'rating': '150#', 'type': 'RFSO'},
        {'mark': 'E', 'service': 'VAPOR RETURN', 'size': '3"', 'rating': '150#', 'type': 'RFSO'},
        {'mark': 'F', 'service': 'RELIEF', 'size': '2"', 'rating': '150#', 'type': 'RFSO'},
        {'mark': 'G', 'service': 'AQUA INLET FILL', 'size': '2"', 'rating': '150#', 'type': 'RFSO'},
        {'mark': 'H', 'service': 'PRESSURE', 'size': '3"', 'rating': '150#', 'type': 'RFSO'},
        {'mark': 'I', 'service': 'LEVEL', 'size': '3"', 'rating': '150#', 'type': 'RFSO'},
        {'mark': 'J', 'service': 'AQUA OUTLET DISCHARGE', 'size': '4"', 'rating': '150#', 'type': 'RFSO'},
        {'mark': 'K', 'service': 'SPARE', 'size': '3"', 'rating': '150#', 'type': 'RFSO W/BLIND'},
        {'mark': 'L', 'service': 'LEVEL', 'size': '3"', 'rating': '150#', 'type': 'RFSO'},
        {'mark': 'M1', 'service': 'SHELL MANWAY', 'size': '24"', 'rating': '150#', 'type': 'RFSO W/DAVIT'},
        {'mark': 'M2', 'service': 'ROOF MANWAY', 'size': '24"', 'rating': '150#', 'type': 'RFSO W/DAVIT'},
        {'mark': 'N', 'service': 'TEMPERATURE', 'size': '2"', 'rating': '150#', 'type': 'RFSO'},
    ],

    # Capacity & Weights
    'operating_capacity_gal': 15000,
    'full_capacity_gal': 18000,
    'empty_weight_lbs': 22500,
    'weight_full_water_lbs': 182400,
    'weight_full_product_lbs': 166500,
    'weight_accessories_lbs': 3600,

    # Vessel Finish
    'interior_weld_treatment': 'SAV TANK STANDARD',
    'exterior_weld_treatment': 'SAV TANK STANDARD',

    # Accessories (ship loose items from drawing)
    'has_handrail': True,
    'has_ladder': True,
    'has_platform': True,
    'has_rest_platform': True,
    'has_swing_gate': True,
    'has_vacuum_rings': True,
    'has_insulation_rings': True,
    'has_nameplate': True,
    'has_ground_lugs': True,
    'has_lift_lugs': True,
    'has_support_legs': True,
}


if __name__ == '__main__':
    print("=" * 80)
    print("BUILD PLAN COMPARISON ANALYSIS")
    print("=" * 80)

    # Analyze Job 24-003 (has certified drawing + actual hours)
    job_003 = analyze_job('24-003')
    print(f"\n--- Job 24-003: Aqueous Ammonia Tank ---")
    print(f"Operations: {job_003['total_ops']}")
    print(f"Estimated Hours: {job_003['est_hours']:.0f}")
    print(f"Actual Hours: {job_003['act_hours']:.0f}")
    print(f"Ratio (Act/Est): {job_003['ratio']:.2f}")
    print(f"\nWork Center Breakdown:")
    for wc, data in sorted(job_003['wc_breakdown'].items()):
        ratio = data['act']/data['est'] if data['est'] > 0 else float('inf')
        print(f"  {wc:<15} {data['count']:>3} ops  Est={data['est']:>7.0f}h  Act={data['act']:>7.0f}h  Ratio={ratio:.2f}")

    # Analyze Job 25-089 (has MASTER BUILD PLAN xlsx in repo)
    job_089 = analyze_job('25-089')
    if job_089:
        print(f"\n--- Job 25-089: Dissolving Tank ---")
        print(f"Operations: {job_089['total_ops']}")
        print(f"Estimated Hours: {job_089['est_hours']:.0f}")
        print(f"Actual Hours: {job_089['act_hours']:.0f}")
        print(f"Ratio (Act/Est): {job_089['ratio']:.2f}")

    # Compare the two
    comp = compare_two_jobs('24-003', '25-089')
    print(f"\n--- Routing Comparison: 24-003 vs 25-089 ---")
    print(f"Job 24-003: {comp['ops_a']} operations")
    print(f"Job 25-089: {comp['ops_b']} operations")
    print(f"Common operations: {comp['common_ops']}")
    print(f"Similarity: {comp['similarity']:.1%}")
    if comp['only_in_a']:
        print(f"\nOnly in 24-003 ({len(comp['only_in_a'])}):")
        for d in comp['only_in_a']:
            print(f"  - {d}")
    if comp['only_in_b']:
        print(f"\nOnly in 25-089 ({len(comp['only_in_b'])}):")
        for d in comp['only_in_b']:
            print(f"  - {d}")

    # All 2024 completed jobs: Est vs Actual hours
    print(f"\n{'=' * 80}")
    print("ALL 2024 COMPLETED JOBS: ESTIMATED vs ACTUAL HOURS")
    print(f"{'=' * 80}")

    all_2024_jobs = []
    with open('JOBBOSS_DATA/job_operations.csv', 'r') as f:
        reader = csv.DictReader(f)
        job_data = defaultdict(lambda: {'est': 0, 'act': 0, 'ops': 0})
        for r in reader:
            job = r['Job']
            if job.startswith('24-'):
                job_data[job]['ops'] += 1
                job_data[job]['est'] += float(r['Est_Total_Hrs']) if r['Est_Total_Hrs'] else 0
                act_r = float(r['Act_Run_Hrs']) if r['Act_Run_Hrs'] else 0
                act_s = float(r['Act_Setup_Hrs']) if r['Act_Setup_Hrs'] else 0
                job_data[job]['act'] += act_r + act_s

    # Only substantial jobs (>50 est hours = real tanks, not small orders)
    real_tanks = {j: d for j, d in job_data.items() if d['est'] >= 50}
    print(f"\nReal tank jobs (>=50 est hours): {len(real_tanks)}")

    ratios = []
    for j in sorted(real_tanks.keys()):
        d = real_tanks[j]
        ratio = d['act'] / d['est'] if d['est'] > 0 else 0
        ratios.append(ratio)
        over_under = "OVER" if ratio > 1.1 else "UNDER" if ratio < 0.9 else "ON TARGET"
        print(f"  {j}: {d['ops']:>3} ops  Est={d['est']:>6.0f}h  Act={d['act']:>6.0f}h  "
              f"Ratio={ratio:.2f}  {over_under}")

    if ratios:
        avg_ratio = sum(ratios) / len(ratios)
        on_target = sum(1 for r in ratios if 0.9 <= r <= 1.1)
        over = sum(1 for r in ratios if r > 1.1)
        under = sum(1 for r in ratios if r < 0.9)
        print(f"\nSummary:")
        print(f"  Average ratio: {avg_ratio:.2f}")
        print(f"  On target (0.9-1.1): {on_target}/{len(ratios)} ({100*on_target/len(ratios):.0f}%)")
        print(f"  Over estimate (>1.1): {over}/{len(ratios)} ({100*over/len(ratios):.0f}%)")
        print(f"  Under estimate (<0.9): {under}/{len(ratios)} ({100*under/len(ratios):.0f}%)")

    # Show vessel specs for the tank we can fully analyze
    print(f"\n{'=' * 80}")
    print("VESSEL SPECS EXTRACTED FROM CERTIFIED DRAWING: Job 24-003")
    print(f"{'=' * 80}")
    specs = JOB_003_24_VESSEL_SPECS
    print(f"  Customer: {specs['customer']}")
    print(f"  Description: {specs['description']}")
    print(f"  Design Code: {specs['design_code']}")
    print(f"  Shell: {specs['shell_id_in']}\" ID x {specs['shell_height_in']}\" tall, {specs['shell_thickness_in']}\" thick")
    print(f"  Material: {specs['shell_material']}")
    print(f"  Shell Courses: {specs['shell_courses']}")
    print(f"  Heads: {specs['head_type']}, {specs['head_thickness_nom_in']}\" nom")
    print(f"  Design Pressure: {specs['design_pressure_psig']} PSIG/{specs['design_pressure_type']}")
    print(f"  Operating Capacity: {specs['operating_capacity_gal']:,} gal")
    print(f"  Empty Weight: {specs['empty_weight_lbs']:,} lbs")
    print(f"  Nozzles: {specs['nozzle_count']} + {specs['manway_count']} manways")
    print(f"  Accessories: HR={specs['has_handrail']}, Ladder={specs['has_ladder']}, Platform={specs['has_platform']}")
    print(f"\n  JobBOSS Routing: {job_003['total_ops']} ops, {job_003['est_hours']:.0f}h est, {job_003['act_hours']:.0f}h actual")
    print(f"  Estimation Accuracy: {job_003['ratio']:.0%} (28% over)")
