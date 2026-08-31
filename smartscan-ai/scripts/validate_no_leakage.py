#!/usr/bin/env python3
"""
validate_no_leakage.py
======================
Validates zero data leakage across 7 strict data boundaries.
Returns exit code 0 if all tests PASS, non-zero on failure.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.evaluation.leakage import LeakageValidator

def main():
    print("=" * 60)
    print("SMARTSCAN AI — DATA LEAKAGE PREVENTION VALIDATION")
    print("=" * 60)

    report = LeakageValidator.validate_all()
    res = report.to_dict()

    print(f"1. Future Data Access       : {res['future_leakage']}")
    print(f"2. Unselected Frequency Bin : {res['frequency_leakage']}")
    print(f"3. Label / Annotation Access: {res['label_leakage']}")
    print(f"4. Train/Test Split Overlap : {res['split_overlap']}")
    print(f"5. Scheduler Visibility     : {res['scheduler_visibility']}")
    print(f"6. Future Periodicity       : {res['future_periodicity']}")
    print(f"7. Future Information Gain  : {res['future_infogain']}")

    print("=" * 60)
    if res['overall_status'] == 'PASS':
        print("OVERALL LEAKAGE STATUS: PASS (Zero Data Leakage Guaranteed)")
        print("=" * 60)
        sys.exit(0)
    else:
        print(f"OVERALL LEAKAGE STATUS: FAIL (Violations: {res['violations']})")
        print("=" * 60)
        sys.exit(1)

if __name__ == "__main__":
    main()
