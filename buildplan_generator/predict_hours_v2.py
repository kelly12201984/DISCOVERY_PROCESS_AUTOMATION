"""
Hours predictor v2 — Estimate Calibration approach.

Instead of predicting hours from scratch, learns the actual/estimated ratio
from sibling jobs and applies it to the target job's existing estimates.

Why this is better:
  - The routing already encodes 90%+ of the right info (Dustin/David's estimates)
  - We only need to correct systematic bias, not predict from zero
  - Works per-operation AND at the job level
  - Handles scale naturally (big tank estimates stay big, small stay small)

Fallback chain:
  1. Per-operation calibration ratio from siblings with same op code
  2. Per-work-center calibration ratio from siblings
  3. Job-level calibration ratio from all siblings
  4. Identity (keep original estimate)
"""
import pandas as pd
import numpy as np
from config import CLEAN_OPS, CLEAN_JOBS, JOBBOSS_DIR, MIN_JOBS_FOR_PREDICTION


def _load_coded_ops():
    ops_file = JOBBOSS_DIR / "Operations.csv"
    if not ops_file.exists():
        return pd.DataFrame()
    return pd.read_csv(ops_file, header=None, encoding="utf-8-sig",
                       names=["Job", "Sequence", "op_code", "Description",
                              "Work_Center", "Est_Total_Hrs", "Act_Total_Hrs",
                              "Status", "Sched_Start"])


class CalibratedPredictor:
    def __init__(self):
        self.ops = pd.read_csv(CLEAN_OPS, low_memory=False)
        if "Act_Total_Hrs" not in self.ops.columns:
            self.ops["Act_Total_Hrs"] = self.ops.get("Act_Run_Hrs", 0)

        self.coded_ops = _load_coded_ops()
        self.jobs = pd.read_csv(CLEAN_JOBS)

        # Pre-compute job-level calibration ratios
        self._compute_job_ratios()

    def _compute_job_ratios(self):
        """Compute actual/estimated ratio per job."""
        completed = self.jobs[
            (self.jobs["Status"].isin(["Complete", "Closed"])) &
            (self.jobs["Est_Total_Hrs"] > 5) &
            (self.jobs["Act_Total_Hrs"] > 5)
        ].copy()
        completed["cal_ratio"] = completed["Act_Total_Hrs"] / completed["Est_Total_Hrs"]
        # Clip extreme ratios
        completed["cal_ratio"] = completed["cal_ratio"].clip(0.2, 5.0)
        self.job_ratios = dict(zip(completed["Job"], completed["cal_ratio"]))

    def predict_from_siblings(self, sibling_jobs: list[str],
                              target_ops: pd.DataFrame) -> pd.DataFrame:
        """Calibrate each operation's estimated hours using sibling ratios.

        For each target operation:
          1. Find same op_code in siblings, compute median(actual/estimated) ratio
          2. Apply ratio to target's estimated hours
          3. Fallback to work-center or job-level ratio
        """
        # Compute sibling calibration data
        sib_job_ratios = [self.job_ratios.get(j, 1.0) for j in sibling_jobs if j in self.job_ratios]
        job_level_ratio = np.median(sib_job_ratios) if sib_job_ratios else 1.0

        # Per-op-code ratios from coded ops
        op_ratios = {}
        wc_ratios = {}
        if not self.coded_ops.empty:
            sib_coded = self.coded_ops[self.coded_ops["Job"].isin(sibling_jobs)].copy()
            sib_coded["Est_Total_Hrs"] = pd.to_numeric(sib_coded["Est_Total_Hrs"], errors="coerce")
            sib_coded["Act_Total_Hrs"] = pd.to_numeric(sib_coded["Act_Total_Hrs"], errors="coerce")

            # Per op_code ratio
            for code, group in sib_coded.groupby("op_code"):
                code = str(code).strip()
                valid = group[(group["Est_Total_Hrs"] > 0) & (group["Act_Total_Hrs"] > 0)]
                if len(valid) >= 1:
                    ratios = valid["Act_Total_Hrs"] / valid["Est_Total_Hrs"]
                    ratios = ratios.clip(0.2, 5.0)
                    op_ratios[code] = {
                        "ratio": ratios.median(),
                        "n": len(valid),
                        "range": (ratios.min(), ratios.max()),
                        "jobs": valid["Job"].unique().tolist(),
                    }

            # Per work center ratio
            for wc, group in sib_coded.groupby("Work_Center"):
                wc = str(wc).strip().upper()
                valid = group[(group["Est_Total_Hrs"] > 0) & (group["Act_Total_Hrs"] > 0)]
                if len(valid) >= 2:
                    ratios = valid["Act_Total_Hrs"] / valid["Est_Total_Hrs"]
                    wc_ratios[wc] = ratios.clip(0.2, 5.0).median()

        # Also compute per-op-code ratios from clean_ops (description-based)
        sib_ops = self.ops[self.ops["Job"].isin(sibling_jobs)].copy()
        desc_ratios = {}
        for desc, group in sib_ops.groupby("Description"):
            desc_key = str(desc).strip().lower()
            valid = group[(group["Est_Total_Hrs"] > 0) & (group["Act_Total_Hrs"] > 0)]
            if len(valid) >= 1:
                ratios = valid["Act_Total_Hrs"] / valid["Est_Total_Hrs"]
                desc_ratios[desc_key] = ratios.clip(0.2, 5.0).median()

        # Apply calibration to each target operation
        results = []
        for _, op in target_ops.iterrows():
            op_code = str(op.get("op_code", "")).strip()
            desc_key = str(op.get("description", "")).strip().lower()
            wc = str(op.get("work_center", "")).strip().upper()
            est_hrs = float(op.get("est_hours", 0))

            # Skip zero-hour ops (inspections, holds, etc.)
            if est_hrs <= 0:
                results.append(self._build_result(op, 0, "skip", "0h estimate", [], 0, 1.0))
                continue

            # Priority 1: exact op_code ratio from siblings
            if op_code in op_ratios and not op_code.startswith(".S"):
                r = op_ratios[op_code]
                if r["n"] >= MIN_JOBS_FOR_PREDICTION:
                    predicted = est_hrs * r["ratio"]
                    results.append(self._build_result(
                        op, predicted, "high",
                        f"ratio={r['ratio']:.2f} ({r['range'][0]:.2f}-{r['range'][1]:.2f})",
                        r["jobs"], r["n"], r["ratio"]
                    ))
                    continue
                elif r["n"] >= 1:
                    predicted = est_hrs * r["ratio"]
                    results.append(self._build_result(
                        op, predicted, "medium",
                        f"ratio={r['ratio']:.2f} (n={r['n']})",
                        r["jobs"], r["n"], r["ratio"]
                    ))
                    continue

            # Priority 2: description-based ratio
            if desc_key in desc_ratios:
                ratio = desc_ratios[desc_key]
                predicted = est_hrs * ratio
                results.append(self._build_result(
                    op, predicted, "medium",
                    f"desc_ratio={ratio:.2f}",
                    ["desc_match"], 1, ratio
                ))
                continue

            # Priority 3: work center ratio
            if wc in wc_ratios:
                ratio = wc_ratios[wc]
                predicted = est_hrs * ratio
                results.append(self._build_result(
                    op, predicted, "low",
                    f"wc_ratio={ratio:.2f}",
                    ["wc_avg"], 0, ratio
                ))
                continue

            # Priority 4: job-level ratio
            predicted = est_hrs * job_level_ratio
            results.append(self._build_result(
                op, predicted, "low",
                f"job_ratio={job_level_ratio:.2f}",
                [f"job_avg({len(sib_job_ratios)})"], 0, job_level_ratio
            ))

        return pd.DataFrame(results)

    @staticmethod
    def _build_result(op, predicted, confidence, hr_range, source_jobs, n_sources, ratio):
        return {
            **op.to_dict(),
            "predicted_hours": round(predicted, 1),
            "confidence": confidence,
            "sibling_range": hr_range,
            "source_jobs": ", ".join(str(j) for j in source_jobs[:5]),
            "n_sources": n_sources,
            "calibration_ratio": round(ratio, 3),
        }
