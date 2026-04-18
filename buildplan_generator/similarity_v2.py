"""
Spec-based similarity engine (v2).
Matches jobs using physical tank specs instead of circular routing features.

Features used (all available BEFORE routing/build plan exists):
  - material_grade (one-hot encoded)
  - max_plate_thickness
  - plate_count
  - nozzle_count
  - flange_count
  - max_flange_size
  - head_count
  - has_code_stamp
  - total_material_cost
  - Total_Price (scope proxy)
  - capacity_gal
  - tank_type (one-hot encoded)
  - is_batch
  - batch_size
  - certs_required_count
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from config import DATA_DIR, DEFAULT_K_NEIGHBORS


NUMERIC_FEATURES = [
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

CATEGORICAL_FEATURES = ["material_grade", "tank_type"]


class SpecSimilarityEngine:
    def __init__(self, specs_path: str = None):
        self.specs = pd.read_csv(specs_path or (DATA_DIR / "tank_specs.csv"))
        self._prepare()

    def _prepare(self):
        df = self.specs.copy()

        # One-hot encode categoricals
        for col in CATEGORICAL_FEATURES:
            dummies = pd.get_dummies(df[col], prefix=col, dtype=float)
            df = pd.concat([df, dummies], axis=1)

        # Collect feature columns
        dummy_cols = [c for c in df.columns
                      if any(c.startswith(f"{cat}_") for cat in CATEGORICAL_FEATURES)]
        self.feature_cols = NUMERIC_FEATURES + dummy_cols

        # Only keep jobs with some spec data
        has_data = (df["plate_count"] > 0) | (df["Total_Price"] > 0) | (df["nozzle_count"] > 0)
        self.active = df[has_data].copy()
        self.active_specs = self.specs[has_data].copy()

        # Build numeric matrix
        X = self.active[self.feature_cols].fillna(0).values.astype(float)

        self.scaler = StandardScaler()
        self.X_scaled = self.scaler.fit_transform(X)

        n_neighbors = min(DEFAULT_K_NEIGHBORS * 4, len(self.active))
        self.nn = NearestNeighbors(n_neighbors=n_neighbors, metric="euclidean")
        self.nn.fit(self.X_scaled)

        # Keep one-hot df for query building
        self._df_with_dummies = df

    def _build_query_vector(self, row: pd.Series) -> np.ndarray:
        """Build a feature vector from a single row, handling one-hot encoding."""
        vec = []
        for col in NUMERIC_FEATURES:
            vec.append(float(row.get(col, 0) or 0))

        for cat in CATEGORICAL_FEATURES:
            val = row.get(cat, "")
            for fc in self.feature_cols:
                if fc.startswith(f"{cat}_"):
                    vec.append(1.0 if fc == f"{cat}_{val}" else 0.0)

        return np.array([vec])

    def find_similar(self, job_no: str = None, specs_dict: dict = None,
                     k: int = DEFAULT_K_NEIGHBORS,
                     same_type_only: bool = True,
                     exclude_batch_siblings: bool = False) -> pd.DataFrame:
        """Find K most similar jobs by physical specs.

        Args:
            job_no: Look up existing job.
            specs_dict: Or provide specs for a new/unseen job.
            k: Number of neighbors.
            same_type_only: Prefer same tank_type.
            exclude_batch_siblings: Skip same-batch jobs (e.g., other "BUFFER TANK X of 224").
        """
        if job_no:
            row = self.active_specs[self.active_specs["Job"] == job_no]
            if row.empty:
                raise ValueError(f"Job {job_no} not in specs table")
            row = row.iloc[0]
            query_vec = self._build_query_vector(row)
            query_type = row.get("tank_type", "unknown")
            exclude = {job_no}
        elif specs_dict:
            query_vec = self._build_query_vector(pd.Series(specs_dict))
            query_type = specs_dict.get("tank_type", "unknown")
            exclude = set()
        else:
            raise ValueError("Provide either job_no or specs_dict")

        query_scaled = self.scaler.transform(query_vec)

        n_fetch = min(k * 6, len(self.active))
        distances, indices = self.nn.kneighbors(query_scaled, n_neighbors=n_fetch)

        results = self.active_specs.iloc[indices[0]].copy()
        results["similarity_distance"] = distances[0]

        # Exclude self
        results = results[~results["Job"].isin(exclude)]

        # Optionally exclude batch siblings
        if exclude_batch_siblings and job_no:
            query_desc = str(row.get("Description", ""))
            query_cust = str(row.get("Customer", ""))
            is_batch_job = bool(row.get("is_batch", False))
            if is_batch_job:
                results = results[~(
                    (results["Customer"] == query_cust) &
                    (results["is_batch"] == True)
                )]

        # Same type preference
        if same_type_only and query_type not in ("unknown", "other"):
            same = results[results["tank_type"] == query_type]
            if len(same) >= k:
                return same.head(k).reset_index(drop=True)

        return results.head(k).reset_index(drop=True)

    def get_job_specs(self, job_no: str) -> dict:
        row = self.active_specs[self.active_specs["Job"] == job_no]
        if row.empty:
            return {}
        return row.iloc[0].to_dict()
