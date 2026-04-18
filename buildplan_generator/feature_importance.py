"""
Feature importance analysis.
Answers: "Which tank specs contribute most to predicting actual hours?"

Uses gradient boosting regression on the tank_specs feature table.
Reports feature importance rankings and cross-validated accuracy.
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import LabelEncoder
from config import DATA_DIR


def main():
    specs = pd.read_csv(DATA_DIR / "tank_specs.csv")

    # Filter to jobs with actual hours (completed work)
    df = specs[
        (specs["Act_Total_Hrs"] > 10) &
        (specs["Est_Total_Hrs"] > 5) &
        (specs["Status"].isin(["Complete", "Closed"]))
    ].copy()

    print(f"Jobs with actuals for training: {len(df)}")

    # Encode categoricals
    le_mat = LabelEncoder()
    le_type = LabelEncoder()
    le_cust = LabelEncoder()
    df["material_code"] = le_mat.fit_transform(df["material_grade"].fillna("UNKNOWN"))
    df["type_code"] = le_type.fit_transform(df["tank_type"].fillna("other"))
    df["customer_code"] = le_cust.fit_transform(df["Customer"].fillna(""))

    feature_cols = [
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
        "Est_Total_Hrs",
        "material_code",
        "type_code",
        "customer_code",
    ]

    X = df[feature_cols].fillna(0).values
    y = df["Act_Total_Hrs"].values

    # --- Model 1: Predict actual hours directly ---
    print(f"\n{'='*60}")
    print("MODEL 1: Predict actual hours from specs")
    print(f"{'='*60}")

    model = GradientBoostingRegressor(
        n_estimators=200, max_depth=4, learning_rate=0.1,
        min_samples_leaf=5, random_state=42
    )
    model.fit(X, y)

    # Cross-validated R² and MAE
    r2_scores = cross_val_score(model, X, y, cv=5, scoring="r2")
    mae_scores = -cross_val_score(model, X, y, cv=5, scoring="neg_mean_absolute_error")
    mape_scores = []
    from sklearn.model_selection import KFold
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    for train_idx, test_idx in kf.split(X):
        m = GradientBoostingRegressor(n_estimators=200, max_depth=4, learning_rate=0.1,
                                       min_samples_leaf=5, random_state=42)
        m.fit(X[train_idx], y[train_idx])
        preds = m.predict(X[test_idx])
        mape = np.mean(np.abs(y[test_idx] - preds) / y[test_idx]) * 100
        mape_scores.append(mape)

    print(f"\n  Cross-validated R²:    {np.mean(r2_scores):.3f} (±{np.std(r2_scores):.3f})")
    print(f"  Cross-validated MAE:   {np.mean(mae_scores):.1f}h (±{np.std(mae_scores):.1f})")
    print(f"  Cross-validated MAPE:  {np.mean(mape_scores):.1f}% (±{np.std(mape_scores):.1f}%)")

    # Feature importance
    importances = model.feature_importances_
    feat_imp = sorted(zip(feature_cols, importances), key=lambda x: x[1], reverse=True)

    print(f"\n  FEATURE IMPORTANCE (what drives actual hours):")
    print(f"  {'Feature':30s} {'Importance':>12s} {'Cumulative':>12s}")
    print(f"  {'-'*30} {'-'*12} {'-'*12}")
    cum = 0
    for feat, imp in feat_imp:
        cum += imp
        bar = "█" * int(imp * 50)
        print(f"  {feat:30s} {imp:>11.1%} {cum:>11.1%}  {bar}")

    # --- Model 2: Predict calibration ratio ---
    print(f"\n{'='*60}")
    print("MODEL 2: Predict calibration ratio (actual/estimated)")
    print(f"{'='*60}")

    df["cal_ratio"] = df["Act_Total_Hrs"] / df["Est_Total_Hrs"]
    df["cal_ratio"] = df["cal_ratio"].clip(0.2, 5.0)

    y_ratio = df["cal_ratio"].values
    # Remove Est_Total_Hrs from features for ratio prediction (it's in the denominator)
    ratio_cols = [c for c in feature_cols if c != "Est_Total_Hrs"]
    X_ratio = df[ratio_cols].fillna(0).values

    model_ratio = GradientBoostingRegressor(
        n_estimators=200, max_depth=3, learning_rate=0.05,
        min_samples_leaf=5, random_state=42
    )
    model_ratio.fit(X_ratio, y_ratio)

    r2_ratio = cross_val_score(model_ratio, X_ratio, y_ratio, cv=5, scoring="r2")
    print(f"\n  Cross-validated R² for ratio: {np.mean(r2_ratio):.3f} (±{np.std(r2_ratio):.3f})")
    print(f"  Mean ratio: {y_ratio.mean():.3f} (std: {y_ratio.std():.3f})")

    imp_ratio = sorted(zip(ratio_cols, model_ratio.feature_importances_), key=lambda x: x[1], reverse=True)
    print(f"\n  WHAT DRIVES THE ESTIMATE-TO-ACTUAL GAP:")
    print(f"  {'Feature':30s} {'Importance':>12s}")
    print(f"  {'-'*30} {'-'*12}")
    for feat, imp in imp_ratio[:10]:
        bar = "█" * int(imp * 50)
        print(f"  {feat:30s} {imp:>11.1%}  {bar}")

    # --- Summary insights ---
    print(f"\n{'='*60}")
    print("KEY INSIGHTS")
    print(f"{'='*60}")

    # Average ratio by material grade
    print(f"\n  Calibration ratio by material grade (actual/estimated):")
    for grade, group in df.groupby("material_grade"):
        if len(group) >= 3:
            ratio = group["cal_ratio"].median()
            direction = "OVER-estimated" if ratio < 1 else "UNDER-estimated"
            print(f"    {grade:12s}: {ratio:.2f}x  ({direction}, n={len(group)})")

    # Average ratio by tank type
    print(f"\n  Calibration ratio by tank type:")
    for ttype, group in df.groupby("tank_type"):
        if len(group) >= 3:
            ratio = group["cal_ratio"].median()
            direction = "OVER-estimated" if ratio < 1 else "UNDER-estimated"
            print(f"    {ttype:20s}: {ratio:.2f}x  ({direction}, n={len(group)})")

    print()


if __name__ == "__main__":
    main()
