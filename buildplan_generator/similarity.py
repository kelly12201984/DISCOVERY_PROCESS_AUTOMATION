"""
k-NN similarity engine.
Given a new job's features (or a job number to look up), find the K most
similar historical jobs based on operation pattern and estimated hours.
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from config import JOB_FEATURES, DEFAULT_K_NEIGHBORS


# Numeric columns used for similarity matching
SIMILARITY_COLS = [
    "n_operations", "n_ops_with_hours", "total_est_hrs",
    "has_manway", "has_skirt", "has_ladder", "has_handrail",
    "has_platform", "has_jacket", "has_coil", "has_baffles",
    "has_cladding", "has_dip_tubes", "has_stiffeners", "has_body_flange",
]

# Work-center hour columns get added dynamically
WC_PREFIX = "wc_hrs_"


class JobSimilarityEngine:
    def __init__(self, features_path: str = None):
        self.features = pd.read_csv(features_path or JOB_FEATURES)
        self._prepare()

    def _prepare(self):
        wc_cols = [c for c in self.features.columns if c.startswith(WC_PREFIX)]
        self.feature_cols = SIMILARITY_COLS + wc_cols

        # Only use jobs that have actual routing data
        mask = self.features["n_operations"] > 0
        self.active = self.features[mask].copy()

        # Build numeric matrix
        X = self.active[self.feature_cols].fillna(0).values.astype(float)

        self.scaler = StandardScaler()
        self.X_scaled = self.scaler.fit_transform(X)

        self.nn = NearestNeighbors(n_neighbors=min(DEFAULT_K_NEIGHBORS * 2, len(self.active)),
                                   metric="euclidean")
        self.nn.fit(self.X_scaled)

    def find_similar(self, job_no: str = None, features_dict: dict = None,
                     k: int = DEFAULT_K_NEIGHBORS,
                     same_type_only: bool = True) -> pd.DataFrame:
        """Find K most similar jobs.

        Args:
            job_no: Lookup by existing job number.
            features_dict: Or provide a feature dict for a new (unseen) job.
            k: Number of neighbors.
            same_type_only: If True, prefer same tank_type first.

        Returns:
            DataFrame of similar jobs with distance scores.
        """
        if job_no:
            row = self.active[self.active["Job"] == job_no]
            if row.empty:
                raise ValueError(f"Job {job_no} not found in feature table")
            query_vec = row[self.feature_cols].fillna(0).values.astype(float)
            query_type = row.iloc[0]["tank_type"]
            query_scaled = self.scaler.transform(query_vec)
            # Exclude the query job itself from results
            exclude = {job_no}
        elif features_dict:
            query_vec = np.array([[features_dict.get(c, 0) for c in self.feature_cols]])
            query_type = features_dict.get("tank_type", "unknown")
            query_scaled = self.scaler.transform(query_vec)
            exclude = set()
        else:
            raise ValueError("Provide either job_no or features_dict")

        # Get more neighbors than needed, then filter
        n_fetch = min(k * 4, len(self.active))
        distances, indices = self.nn.kneighbors(query_scaled, n_neighbors=n_fetch)

        results = self.active.iloc[indices[0]].copy()
        results["similarity_distance"] = distances[0]
        results["similarity_rank"] = range(1, len(results) + 1)

        # Exclude query job
        results = results[~results["Job"].isin(exclude)]

        # If same_type_only, prioritize same tank type
        if same_type_only and query_type != "unknown":
            same_type = results[results["tank_type"] == query_type]
            if len(same_type) >= k:
                return same_type.head(k)

        return results.head(k)

    def get_job_features(self, job_no: str) -> dict:
        row = self.active[self.active["Job"] == job_no]
        if row.empty:
            return {}
        return row.iloc[0].to_dict()
