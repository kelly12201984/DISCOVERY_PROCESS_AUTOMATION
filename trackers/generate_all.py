"""
Generate All Trackers from JobBOSS Data
Run this to regenerate all tracker spreadsheets from the CSV exports.

Usage: python trackers/generate_all.py
"""
import subprocess
import sys
import os

SCRIPTS = [
    ('Released Jobs Tracker (April)',    'generate_released_jobs.py'),
    ('Ops Priority List (Dustin)',       'generate_ops_priority.py'),
    ('Weekly Efficiency Tracker (Dustin)','generate_efficiency.py'),
    ('Missing POs Tracker (John)',       'generate_missing_pos.py'),
    ('Master Schedule (April)',          'generate_master_schedule.py'),
]

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print("=" * 60)
    print("Generating all trackers from JobBOSS data")
    print("=" * 60)

    for label, script in SCRIPTS:
        print(f"\n--- {label} ---")
        result = subprocess.run(
            [sys.executable, os.path.join(script_dir, script)],
            capture_output=True, text=True,
            cwd=os.path.join(script_dir, '..')
        )
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(f"ERROR: {result.stderr}")

    print("\n" + "=" * 60)
    print("Done. Output in: generated_trackers/")
    print("=" * 60)

if __name__ == '__main__':
    main()
