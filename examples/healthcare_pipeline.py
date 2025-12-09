#!/usr/bin/env python3
"""
Healthcare Data Pipeline Example.

This example demonstrates a realistic healthcare data processing
pipeline with multiple DataFrames, joins, and transformations.
"""

import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

# Add parent directory to path for local development
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas_flow


def generate_healthcare_data():
    """Generate realistic healthcare sample data."""
    np.random.seed(42)

    # Generate patient demographics
    n_patients = 5000
    patients = pd.DataFrame(
        {
            "patient_id": [f"P{i:05d}" for i in range(1, n_patients + 1)],
            "birth_date": pd.date_range("1930-01-01", "2010-12-31", periods=n_patients),
            "gender": np.random.choice(
                ["Male", "Female", "Other"], n_patients, p=[0.48, 0.50, 0.02]
            ),
            "blood_type": np.random.choice(
                ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"], n_patients
            ),
            "insurance_type": np.random.choice(
                ["Private", "Medicare", "Medicaid", "None"], n_patients, p=[0.5, 0.25, 0.15, 0.1]
            ),
        }
    )

    # Calculate age
    today = datetime.now()
    patients["age"] = ((today - patients["birth_date"]).dt.days / 365.25).astype(int)

    # Generate hospital visits
    n_visits = 15000
    visits = pd.DataFrame(
        {
            "visit_id": [f"V{i:06d}" for i in range(1, n_visits + 1)],
            "patient_id": np.random.choice(patients["patient_id"], n_visits),
            "visit_date": pd.date_range("2023-01-01", "2024-12-31", periods=n_visits),
            "department": np.random.choice(
                ["Emergency", "Cardiology", "Oncology", "Neurology", "Orthopedics", "General"],
                n_visits,
                p=[0.25, 0.15, 0.10, 0.10, 0.15, 0.25],
            ),
            "visit_type": np.random.choice(
                ["Inpatient", "Outpatient", "Emergency"], n_visits, p=[0.2, 0.5, 0.3]
            ),
            "duration_hours": np.random.exponential(12, n_visits).round(1),
            "cost": np.random.exponential(2000, n_visits).round(2),
        }
    )

    # Generate lab results
    n_labs = 25000
    labs = pd.DataFrame(
        {
            "lab_id": [f"L{i:06d}" for i in range(1, n_labs + 1)],
            "visit_id": np.random.choice(visits["visit_id"], n_labs),
            "test_name": np.random.choice(
                ["CBC", "BMP", "Lipid Panel", "HbA1c", "TSH", "Urinalysis", "CRP"], n_labs
            ),
            "result_value": np.random.uniform(0, 200, n_labs).round(2),
            "unit": np.random.choice(["mg/dL", "mmol/L", "%", "mIU/L"], n_labs),
            "is_abnormal": np.random.choice([True, False], n_labs, p=[0.15, 0.85]),
        }
    )

    # Generate diagnoses
    n_diagnoses = 20000
    icd_codes = ["I10", "E11", "J06", "M54", "K21", "F32", "N39", "J45", "G43", "L30"]
    diagnoses = pd.DataFrame(
        {
            "diagnosis_id": [f"D{i:06d}" for i in range(1, n_diagnoses + 1)],
            "visit_id": np.random.choice(visits["visit_id"], n_diagnoses),
            "icd_code": np.random.choice(icd_codes, n_diagnoses),
            "description": np.random.choice(
                [
                    "Hypertension",
                    "Type 2 Diabetes",
                    "Upper Respiratory Infection",
                    "Back Pain",
                    "GERD",
                    "Depression",
                    "UTI",
                    "Asthma",
                    "Migraine",
                    "Dermatitis",
                ],
                n_diagnoses,
            ),
            "is_primary": np.random.choice([True, False], n_diagnoses, p=[0.4, 0.6]),
        }
    )

    return patients, visits, labs, diagnoses


def main():
    """Run the healthcare pipeline example."""
    print("=" * 70)
    print("Healthcare Data Pipeline Example")
    print("=" * 70)
    print()

    # Setup tracker with healthcare-specific variables
    flow = pandas_flow.setup(
        track_row_count=True,
        track_variables={
            "patient_id": "n_unique",
            "visit_id": "n_unique",
            "department": "n_unique",
        },
        stats_variable="age",
        stats_types=["min", "max", "mean", "std", "top3_freq", "histogram"],
        theme="default",
    )

    print("Generating sample healthcare data...")
    patients, visits, labs, diagnoses = generate_healthcare_data()

    # Register DataFrames
    for df, name, source in [
        (patients, "patients", "patients.parquet"),
        (visits, "visits", "visits.parquet"),
        (labs, "labs", "lab_results.parquet"),
        (diagnoses, "diagnoses", "diagnoses.parquet"),
    ]:
        flow.register_dataframe(df, name=name, source_file=source)
        flow.record_operation(
            operation_type=pandas_flow.OperationType.READ_PARQUET,
            operation_name=f"Load {name.title()}",
            input_dfs=[],
            output_df=df,
            description=f"Load {name} data from warehouse",
            arguments={"file": source},
        )

    print("Processing pipeline...")
    print()

    # Step 1: Join patients with visits
    patient_visits = patients.merge(visits, on="patient_id", how="inner")

    # Step 2: Filter to recent visits (2024)
    recent_visits = patient_visits.query("visit_date >= '2024-01-01'")

    # Step 3: Filter adults only
    adults_only = recent_visits.query("age >= 18")

    # Step 4: Join with lab results
    with_labs = adults_only.merge(labs, on="visit_id", how="left")

    # Step 5: Join with diagnoses
    full_data = with_labs.merge(diagnoses, on="visit_id", how="left")

    # Step 6: Filter to primary diagnoses
    primary_dx = full_data.query("is_primary == True")

    # Step 7: Drop duplicates
    unique_visits = primary_dx.drop_duplicates(subset=["patient_id", "visit_date"])

    # Step 8: Handle missing values
    clean_data = unique_visits.fillna(
        {
            "result_value": 0,
            "icd_code": "UNKNOWN",
            "description": "Not Specified",
        }
    )

    # Step 9: Add calculated fields
    enriched = clean_data.assign(
        visit_month=clean_data["visit_date"].dt.to_period("M").astype(str),
        age_group=pd.cut(
            clean_data["age"],
            bins=[18, 30, 45, 60, 75, 120],
            labels=["18-29", "30-44", "45-59", "60-74", "75+"],
        ),
        high_cost=clean_data["cost"] > 5000,
    )

    # Step 10: Sort by date
    sorted_data = enriched.sort_values(["visit_date", "patient_id"])

    # Step 11: Drop temporary columns
    final = sorted_data.drop(columns=["is_primary", "is_abnormal"])

    # Print summary
    print("Pipeline Summary:")
    print("-" * 40)
    print(flow.summary())

    # Output
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    # Save flowchart
    md_path = output_dir / "healthcare_pipeline.md"
    flow.render(str(md_path), title="Healthcare Data Pipeline", direction="TB")
    print(f"✓ Flowchart saved to: {md_path}")

    html_path = output_dir / "healthcare_pipeline.html"
    flow.render(str(html_path), title="Healthcare Data Pipeline")
    print(f"✓ HTML version saved to: {html_path}")

    # Print final statistics
    print()
    print("Final Dataset Statistics:")
    print(f"  Rows: {len(final):,}")
    print(f"  Columns: {len(final.columns)}")
    print(f"  Unique Patients: {final['patient_id'].nunique():,}")
    print(f"  Unique Visits: {final['visit_id'].nunique():,}")
    print(f"  Date Range: {final['visit_date'].min().date()} to {final['visit_date'].max().date()}")

    print()
    print("=" * 70)
    print("Healthcare pipeline completed successfully!")
    print("=" * 70)

    return final


if __name__ == "__main__":
    main()
