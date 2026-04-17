"""
Hours predictor.
Phase 1: Sibling-median approach — for each operation, predict hours from the
median actual hours of the K most similar historical jobs.

Uses Operations.csv (with op codes) as primary data source for matching.
Falls back to description matching when op codes aren't available.
"""
import pandas as pd
import numpy as np
from config import CLEAN_OPS, JOBBOSS_DIR, MIN_JOBS_FOR_PREDICTION


def _load_coded_ops():
    """Load the Operations.csv with actual op codes per job."""
    ops_file = JOBBOSS_DIR / "Operations.csv"
    if not ops_file.exists():
        return None
    return pd.read_csv(ops_file, header=None, encoding="utf-8-sig",
                       names=["Job", "Sequence", "op_code", "Description",
                              "Work_Center", "Est_Total_Hrs", "Act_Total_Hrs",
                              "Status", "Sched_Start"])


class HoursPredictor:
    def __init__(self, ops_path: str = None):
        self.ops = pd.read_csv(ops_path or CLEAN_OPS, low_memory=False)
        if "Act_Total_Hrs" not in self.ops.columns:
            self.ops["Act_Total_Hrs"] = self.ops.get("Act_Run_Hrs", 0)

        self.coded_ops = _load_coded_ops()

    def predict_from_siblings(self, sibling_jobs: list[str],
                              target_ops: pd.DataFrame) -> pd.DataFrame:
        """Given a list of sibling job numbers and a target operation list,
        predict hours for each operation using op-code matching.

        Matching priority:
          1. Exact op_code match in sibling operations (from Operations.csv)
          2. Description match in sibling operations (from clean_ops)
          3. Global median for this op code
          4. Fallback to estimate
        """
        # Get sibling ops with codes (preferred)
        if self.coded_ops is not None:
            sib_coded = self.coded_ops[self.coded_ops["Job"].isin(sibling_jobs)].copy()
            sib_coded["op_code"] = sib_coded["op_code"].astype(str).str.strip()
        else:
            sib_coded = pd.DataFrame()

        # Also get from clean_ops as fallback
        sib_ops = self.ops[self.ops["Job"].isin(sibling_jobs)].copy()

        results = []
        for _, op in target_ops.iterrows():
            op_code = str(op.get("op_code", "")).strip()
            desc_key = str(op.get("description", "")).strip().lower()
            wc_key = str(op.get("work_center", "")).strip().upper()

            act_hrs = pd.Series(dtype=float)
            est_hrs_series = pd.Series(dtype=float)
            source_jobs = []

            # Strategy 1: Match by op_code in coded sibling ops
            if not sib_coded.empty and op_code and not op_code.startswith(".S"):
                code_matches = sib_coded[sib_coded["op_code"] == op_code]
                if not code_matches.empty:
                    act_hrs = pd.to_numeric(code_matches["Act_Total_Hrs"], errors="coerce").dropna()
                    act_hrs = act_hrs[act_hrs > 0]
                    est_hrs_series = pd.to_numeric(code_matches["Est_Total_Hrs"], errors="coerce").dropna()
                    source_jobs = code_matches["Job"].unique().tolist()

            # Strategy 2: Match by description in clean_ops
            if len(act_hrs) == 0 and desc_key:
                desc_matches = sib_ops[
                    (sib_ops["Description"].fillna("").str.lower().str.strip() == desc_key) &
                    (sib_ops["Work_Center"].fillna("").str.upper() == wc_key)
                ]
                if desc_matches.empty and len(desc_key) > 15:
                    desc_matches = sib_ops[
                        sib_ops["Description"].fillna("").str.lower().str.strip().str[:20] == desc_key[:20]
                    ]
                if not desc_matches.empty:
                    act_hrs = desc_matches["Act_Total_Hrs"].dropna()
                    act_hrs = act_hrs[act_hrs > 0]
                    est_hrs_series = desc_matches["Est_Total_Hrs"].dropna()
                    source_jobs = desc_matches["Job"].unique().tolist()

            # Strategy 3: Global median by op_code
            if len(act_hrs) == 0 and not sib_coded.empty and op_code and not op_code.startswith(".S"):
                global_coded = self.coded_ops[self.coded_ops["op_code"].astype(str).str.strip() == op_code]
                global_act = pd.to_numeric(global_coded["Act_Total_Hrs"], errors="coerce").dropna()
                global_act = global_act[global_act > 0]
                if len(global_act) > 0:
                    results.append(self._build_result(
                        op, global_act.median(), "low",
                        f"global:{global_act.min():.1f}-{global_act.max():.1f}",
                        ["global"], len(global_act)
                    ))
                    continue

            # Strategy 4: Global by description
            if len(act_hrs) == 0:
                global_desc = self.ops[
                    self.ops["Description"].fillna("").str.lower().str.strip() == desc_key
                ]
                global_act = global_desc["Act_Total_Hrs"].dropna()
                global_act = global_act[global_act > 0]
                if len(global_act) > 0:
                    results.append(self._build_result(
                        op, global_act.median(), "low",
                        f"global:{global_act.min():.1f}-{global_act.max():.1f}",
                        ["global"], len(global_act)
                    ))
                    continue

            # Build result from sibling matches
            if len(act_hrs) >= MIN_JOBS_FOR_PREDICTION:
                results.append(self._build_result(
                    op, act_hrs.median(), "high",
                    f"{act_hrs.min():.1f}-{act_hrs.max():.1f}",
                    source_jobs, len(act_hrs)
                ))
            elif len(act_hrs) > 0:
                results.append(self._build_result(
                    op, act_hrs.median(), "medium",
                    f"{act_hrs.min():.1f}-{act_hrs.max():.1f}",
                    source_jobs, len(act_hrs)
                ))
            elif len(est_hrs_series) > 0:
                results.append(self._build_result(
                    op, est_hrs_series.median(), "low",
                    f"est:{est_hrs_series.min():.1f}-{est_hrs_series.max():.1f}",
                    source_jobs, 0
                ))
            else:
                results.append(self._build_result(
                    op, float(op.get("est_hours", 0)), "none",
                    "no data", [], 0
                ))

        return pd.DataFrame(results)

    @staticmethod
    def _build_result(op, predicted, confidence, hr_range, source_jobs, n_sources):
        return {
            **op.to_dict(),
            "predicted_hours": round(predicted, 1),
            "confidence": confidence,
            "sibling_range": hr_range,
            "source_jobs": ", ".join(str(j) for j in source_jobs[:5]),
            "n_sources": n_sources,
        }
