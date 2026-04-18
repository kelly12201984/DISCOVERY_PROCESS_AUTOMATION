"""
Hybrid similarity engine (v3).
Combines spec-based matching (v2) with operation overlap re-ranking.

At build plan creation time, the job already has:
  - Specs (from BOM/drawings) → physical similarity
  - Routing (from JobBOSS) → operational similarity
  - Price, customer → scope proxy

Strategy: find candidates via specs, re-rank by weighted score combining
spec distance + operation overlap. Best of both worlds.
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from config import DATA_DIR, DEFAULT_K_NEIGHBORS, JOBBOSS_DIR


# --- Feature definitions ---

SPEC_FEATURES = [
    "max_plate_thickness",
    "plate_count",
    "nozzle_count",
    "flange_count",
    "max_flange_size",
    "head_count",
    "has_code_stamp",
    "total_material_cost",
    "Total_Price",
    "capacity_gal",
    "is_batch",
    "batch_size",
    "certs_required_count",
]

ROUTING_FEATURES = [
    "n_operations",
    "Est_Total_Hrs",
]

CATEGORICAL_FEATURES = ["material_grade", "tank_type"]

# Weight: how much spec vs routing matters (0=all routing, 1=all spec)
SPEC_WEIGHT = 0.6
ROUTING_WEIGHT = 0.4


def _load_ops_with_codes():
    ops_file = JOBBOSS_DIR / "Operations.csv"
    if not ops_file.exists():
        return pd.DataFrame()
    return pd.read_csv(ops_file, header=None, encoding="utf-8-sig",
                       names=["Job", "Sequence", "op_code", "Description",
                              "Work_Center", "Est_Total_Hrs", "Act_Total_Hrs",
                              "Status", "Sched_Start"])


class HybridSimilarityEngine:
    def __init__(self, specs_path: str = None, features_path: str = None):
        self.specs = pd.read_csv(specs_path or (DATA_DIR / "tank_specs.csv"))
        self.coded_ops = _load_ops_with_codes()

        # Pre-compute op sets per job for overlap scoring
        self._build_op_index()
        self._prepare()

    def _build_op_index(self):
        """Build a dict of {job: set(op_codes)} for operation overlap."""
        self.job_ops = {}
        if not self.coded_ops.empty:
            for job, group in self.coded_ops.groupby("Job"):
                codes = set(group["op_code"].astype(str).str.strip())
                codes.discard("nan")
                codes.discard("NULL")
                self.job_ops[job] = codes

    def _prepare(self):
        df = self.specs.copy()

        # Add routing features from job_operations count
        from config import CLEAN_OPS
        try:
            ops = pd.read_csv(CLEAN_OPS, low_memory=False)
            op_counts = ops.groupby("Job").agg(
                n_operations=("Sequence", "count"),
            ).reset_index()
            df = df.merge(op_counts, on="Job", how="left")
            df["n_operations"] = df["n_operations"].fillna(0)
        except Exception:
            df["n_operations"] = 0

        # One-hot encode categoricals
        for col in CATEGORICAL_FEATURES:
            dummies = pd.get_dummies(df[col], prefix=col, dtype=float)
            df = pd.concat([df, dummies], axis=1)

        dummy_cols = [c for c in df.columns
                      if any(c.startswith(f"{cat}_") for cat in CATEGORICAL_FEATURES)]
        self.feature_cols = SPEC_FEATURES + ROUTING_FEATURES + dummy_cols

        # Only jobs with data
        has_data = (df["plate_count"] > 0) | (df["Total_Price"] > 0) | (df["n_operations"] > 0)
        self.active = df[has_data].copy()
        self.active_specs = self.specs[has_data].copy()

        X = self.active[self.feature_cols].fillna(0).values.astype(float)
        self.scaler = StandardScaler()
        self.X_scaled = self.scaler.fit_transform(X)

        n_neighbors = min(DEFAULT_K_NEIGHBORS * 6, len(self.active))
        self.nn = NearestNeighbors(n_neighbors=n_neighbors, metric="euclidean")
        self.nn.fit(self.X_scaled)

    def _build_query_vector(self, row: pd.Series) -> np.ndarray:
        vec = []
        for col in SPEC_FEATURES + ROUTING_FEATURES:
            vec.append(float(row.get(col, 0) or 0))
        for cat in CATEGORICAL_FEATURES:
            val = row.get(cat, "")
            for fc in self.feature_cols:
                if fc.startswith(f"{cat}_"):
                    vec.append(1.0 if fc == f"{cat}_{val}" else 0.0)
        return np.array([vec])

    def _op_overlap(self, job_a: str, job_b: str) -> float:
        """Jaccard overlap of operation codes between two jobs."""
        ops_a = self.job_ops.get(job_a, set())
        ops_b = self.job_ops.get(job_b, set())
        if not ops_a or not ops_b:
            return 0.0
        intersection = len(ops_a & ops_b)
        union = len(ops_a | ops_b)
        return intersection / union if union > 0 else 0.0

    def find_similar(self, job_no: str = None, specs_dict: dict = None,
                     k: int = DEFAULT_K_NEIGHBORS,
                     same_type_only: bool = True) -> pd.DataFrame:
        if job_no:
            row = self.active[self.active_specs["Job"].values == job_no]
            if row.empty:
                raise ValueError(f"Job {job_no} not in specs table")
            row_data = row.iloc[0]
            query_vec = self._build_query_vector(row_data)
            query_type = self.active_specs[self.active_specs["Job"] == job_no].iloc[0].get("tank_type", "unknown")
            exclude = {job_no}
        elif specs_dict:
            query_vec = self._build_query_vector(pd.Series(specs_dict))
            query_type = specs_dict.get("tank_type", "unknown")
            exclude = set()
            job_no = None
        else:
            raise ValueError("Provide either job_no or specs_dict")

        query_scaled = self.scaler.transform(query_vec)

        # Get broad candidate pool
        n_fetch = min(k * 8, len(self.active))
        distances, indices = self.nn.kneighbors(query_scaled, n_neighbors=n_fetch)

        candidates = self.active_specs.iloc[indices[0]].copy()
        candidates["spec_distance"] = distances[0]
        candidates = candidates[~candidates["Job"].isin(exclude)]

        if job_no:
            # Re-rank with operation overlap
            candidates["op_overlap"] = candidates["Job"].apply(
                lambda j: self._op_overlap(job_no, j)
            )

            # Normalize distances to [0, 1] range
            max_dist = candidates["spec_distance"].max()
            if max_dist > 0:
                candidates["spec_score"] = 1 - (candidates["spec_distance"] / max_dist)
            else:
                candidates["spec_score"] = 1.0

            # Combined score: higher is better
            candidates["combined_score"] = (
                SPEC_WEIGHT * candidates["spec_score"] +
                ROUTING_WEIGHT * candidates["op_overlap"]
            )
            candidates = candidates.sort_values("combined_score", ascending=False)
        else:
            candidates["op_overlap"] = 0.0
            candidates["combined_score"] = 0.0

        # Rename for compatibility
        candidates["similarity_distance"] = candidates["spec_distance"]

        # Same type preference
        if same_type_only and query_type not in ("unknown", "other"):
            same = candidates[candidates["tank_type"] == query_type]
            if len(same) >= k:
                return same.head(k).reset_index(drop=True)

        return candidates.head(k).reset_index(drop=True)

    def get_job_specs(self, job_no: str) -> dict:
        row = self.active_specs[self.active_specs["Job"] == job_no]
        if row.empty:
            return {}
        return row.iloc[0].to_dict()
