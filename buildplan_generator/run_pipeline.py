"""
Run the full pipeline: clean → parse → features → ready to generate.
Execute this once after refreshing JOBBOSS_DATA exports.
"""
import subprocess
import sys
from pathlib import Path

SCRIPTS = [
    ("Step 1: Clean JobBOSS data", "clean_data.py"),
    ("Step 2: Parse build plans", "parse_build_plans.py"),
    ("Step 3: Extract features & routing catalog", "features.py"),
    ("Step 4: Extract tank specs from BOM + descriptions", "extract_specs.py"),
]


def main():
    base = Path(__file__).resolve().parent

    for label, script in SCRIPTS:
        print(f"\n{'='*60}")
        print(f"  {label}")
        print(f"{'='*60}\n")
        result = subprocess.run(
            [sys.executable, str(base / script)],
            cwd=str(base),
        )
        if result.returncode != 0:
            print(f"\nFAILED at: {label}")
            sys.exit(1)

    print(f"\n{'='*60}")
    print(f"  Pipeline complete! Ready to generate build plans.")
    print(f"{'='*60}")
    print(f"\nUsage:")
    print(f"  python generate.py 089-25           # generate for a job")
    print(f"  python generate.py --backtest 20    # test on last 20 jobs")
    print(f"\nOutput goes to: {base / 'output'}/")


if __name__ == "__main__":
    main()
