"""
Per-group hours prediction using spec features.

Instead of predicting total job hours and distributing, predicts hours for
each operation GROUP independently using the spec features that matter for
that group. Groups are then distributed to individual operations within
each group based on historical proportions.

Groups: NOZZLES, CUT_PREP, SUPPORTS, MISC_PARTS, LADDERS_ETC, SHELLS,
        TOP_HEAD, BTM_HEAD, SKIRT, FIT_ASSEMBLY, DETAIL_EXT, TEST_CLEAN
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import cross_val_predict
from config import DATA_DIR, JOBBOSS_DIR

OP_GROUPS = {
    "NOZZLES":     [".100",".105",".107",".110",".115",".120",".125",".130",".135",".140",".145",".147"],
    "CUT_PREP":    [".150",".155",".156",".160"],
    "SUPPORTS":    [".165",".170",".175",".180",".185"],
    "MISC_PARTS":  [".200",".205",".210",".215",".220",".225",".230",".235",".240",".245",".250",".252",".255",".257",".260",".261"],
    "LADDERS_ETC": [".262",".265",".270",".272",".275",".280",".282",".285",".290",".292",".295"],
    "SHELLS":      [".300",".305",".310",".315",".320",".325",".326"],
    "TOP_HEAD":    [".350",".355",".360",".365",".366",".370",".375",".380",".382",".383",".385",".390",".395"],
    "BTM_HEAD":    [".450",".455",".460",".465",".466",".470",".475",".477",".478",".479",".482",".483",".485",".490",".495"],
    "SKIRT":       [".500",".510",".515",".520",".530",".540",".545"],
    "FIT_ASSEMBLY":[".600",".605",".610",".615",".616",".620",".625",".630",".635",".637",".638",".640",".641",".645"],
    "DETAIL_EXT":  [".700",".705",".710",".711",".715",".717",".720",".721",".725",".726",".730",".735",".740",".745",".750",".755",".760",".765",".770"],
    "TEST_CLEAN":  [".801",".802",".900",".910",".920",".940",".950",".960"],
}

CODE_TO_GROUP = {}
for group, codes in OP_GROUPS.items():
    for c in codes:
        CODE_TO_GROUP[c] = group

SPEC_FEATURES = [
    "max_plate_thickness", "plate_count", "nozzle_count", "flange_count",
    "max_flange_size", "head_count", "has_code_stamp", "total_material_cost",
    "Total_Price", "Est_Total_Hrs",
]

MATERIAL_CODES = {
    "304L": 1, "304": 1, "SA240": 1,
    "316L": 2, "316": 2,
    "SA36": 3, "A36": 3, "CS": 3,
    "SA516": 4,
    "2205": 5, "DUPLEX": 5,
    "904L": 6, "HASTELLOY": 7, "INCONEL": 8,
    "UNKNOWN": 0,
}


class GroupHoursPredictor:
    """Predicts hours per operation group using per-group regression models."""

    def __init__(self):
        self.models = {}
        self.group_op_proportions = {}
        self._trained = False

    def train(self, specs_path: str = None, ops_path: str = None):
        specs = pd.read_csv(specs_path or (DATA_DIR / "tank_specs.csv"))
        ops_file = ops_path or (JOBBOSS_DIR / "Operations.csv")
        ops = pd.read_csv(ops_file, header=None, encoding="utf-8-sig",
                          names=["Job", "Sequence", "op_code", "Description",
                                 "Work_Center", "Est_Hrs", "Act_Hrs", "Status", "Date"])
        ops["Act_Hrs"] = pd.to_numeric(ops["Act_Hrs"], errors="coerce").fillna(0)
        ops["Est_Hrs"] = pd.to_numeric(ops["Est_Hrs"], errors="coerce").fillna(0)

        tank_jobs = set(specs["Job"])
        ops = ops[ops["Job"].isin(tank_jobs)]
        ops["group"] = ops["op_code"].map(CODE_TO_GROUP).fillna("OTHER")

        # Build group-level actual hours per job
        group_hrs = ops.groupby(["Job", "group"])["Act_Hrs"].sum().unstack(fill_value=0)

        # Only train on jobs with actual hours
        completed = specs[specs["Act_Total_Hrs"] > 10].copy()
        completed["material_code"] = completed["material_grade"].map(MATERIAL_CODES).fillna(0)

        merged = completed.merge(group_hrs, left_on="Job", right_index=True, how="inner")
        if len(merged) < 20:
            print(f"  Warning: only {len(merged)} completed jobs for training")
            return

        X = merged[SPEC_FEATURES + ["material_code"]].fillna(0).values

        print(f"Training per-group models on {len(merged)} completed tank jobs...")
        print(f"{'Group':15s} {'R²':>8s} {'MAE':>8s} {'MedianAE':>10s} {'Hrs Share':>10s}")
        print("-" * 55)

        for group_name in OP_GROUPS:
            if group_name not in merged.columns:
                continue
            y = merged[group_name].values
            if y.sum() == 0 or (y > 0).sum() < 10:
                continue

            model = GradientBoostingRegressor(
                n_estimators=100, max_depth=3, learning_rate=0.1,
                min_samples_leaf=5, random_state=42
            )
            model.fit(X, y)

            # Cross-validated performance
            y_pred = cross_val_predict(model, X, y, cv=min(5, len(merged)))
            y_pred = np.maximum(y_pred, 0)
            r2 = 1 - np.sum((y - y_pred)**2) / np.sum((y - y.mean())**2)
            mae = np.mean(np.abs(y - y_pred))
            medae = np.median(np.abs(y[y > 0] - y_pred[y > 0])) if (y > 0).sum() > 0 else 0
            pct = y.sum() / merged[[c for c in OP_GROUPS if c in merged.columns]].sum().sum() * 100

            print(f"{group_name:15s} {r2:>7.2f} {mae:>7.1f}h {medae:>9.1f}h {pct:>9.1f}%")

            self.models[group_name] = model

        # Build within-group operation proportions
        # For each group, what fraction of group hours does each op code get?
        for group_name, codes in OP_GROUPS.items():
            group_ops = ops[(ops["group"] == group_name) & (ops["Act_Hrs"] > 0)]
            if len(group_ops) == 0:
                continue
            total_by_op = group_ops.groupby("op_code")["Act_Hrs"].sum()
            total = total_by_op.sum()
            if total > 0:
                self.group_op_proportions[group_name] = (total_by_op / total).to_dict()

        self._trained = True
        print(f"\nTrained {len(self.models)} group models")

    def predict(self, job_specs: dict) -> dict:
        """Predict hours per operation group for a job.

        Args:
            job_specs: dict with keys from SPEC_FEATURES + material_grade.

        Returns:
            dict: {group_name: predicted_hours}
        """
        if not self._trained:
            raise RuntimeError("Call train() first")

        mat_code = MATERIAL_CODES.get(job_specs.get("material_grade", "UNKNOWN"), 0)
        x = np.array([[
            float(job_specs.get(f, 0) or 0) for f in SPEC_FEATURES
        ] + [mat_code]])

        predictions = {}
        for group_name, model in self.models.items():
            pred = max(0, model.predict(x)[0])
            predictions[group_name] = round(pred, 1)

        return predictions

    def predict_per_operation(self, job_specs: dict, routing: pd.DataFrame) -> pd.DataFrame:
        """Predict hours for each individual operation in a routing.

        Uses group-level predictions distributed proportionally within each group,
        constrained by which operations actually appear in this job's routing.
        """
        group_preds = self.predict(job_specs)

        results = []
        for _, op in routing.iterrows():
            op_code = str(op.get("op_code", "")).strip()
            group = CODE_TO_GROUP.get(op_code, "OTHER")

            group_total = group_preds.get(group, 0)
            if group_total <= 0:
                results.append({
                    **op.to_dict(),
                    "predicted_hours": float(op.get("est_hours", 0)),
                    "confidence": "none",
                    "prediction_source": "fallback_estimate",
                })
                continue

            # Get this op's share of its group
            proportions = self.group_op_proportions.get(group, {})
            op_share = proportions.get(op_code, 0)

            # Normalize share among ops present in THIS routing
            routing_ops_in_group = [
                str(r.get("op_code", "")).strip()
                for _, r in routing.iterrows()
                if CODE_TO_GROUP.get(str(r.get("op_code", "")).strip(), "OTHER") == group
            ]
            total_share = sum(proportions.get(c, 0) for c in routing_ops_in_group)

            if total_share > 0 and op_share > 0:
                normalized_share = op_share / total_share
                predicted = group_total * normalized_share
                confidence = "high" if group in self.models else "low"
            elif len(routing_ops_in_group) > 0:
                predicted = group_total / len(routing_ops_in_group)
                confidence = "medium"
            else:
                predicted = float(op.get("est_hours", 0))
                confidence = "none"

            results.append({
                **op.to_dict(),
                "predicted_hours": round(max(0, predicted), 1),
                "confidence": confidence,
                "prediction_source": f"group:{group}",
                "sibling_range": f"group_total:{group_total:.0f}h",
                "source_jobs": f"model({group})",
                "n_sources": 0,
            })

        return pd.DataFrame(results)


def main():
    predictor = GroupHoursPredictor()
    predictor.train()

    # Quick test: predict for a known job
    specs = pd.read_csv(DATA_DIR / "tank_specs.csv")
    test_job = specs[specs["Act_Total_Hrs"] > 100].iloc[0]
    print(f"\nTest prediction for {test_job['Job']} ({test_job['Description']}):")
    print(f"  Actual total: {test_job['Act_Total_Hrs']:.0f}h, Estimated: {test_job['Est_Total_Hrs']:.0f}h")

    preds = predictor.predict(test_job.to_dict())
    total = sum(preds.values())
    print(f"  Predicted total: {total:.0f}h")
    for g, h in sorted(preds.items(), key=lambda x: -x[1]):
        if h > 0:
            print(f"    {g:15s}: {h:6.1f}h")


if __name__ == "__main__":
    main()
