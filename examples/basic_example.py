#!/usr/bin/env python3
"""
Basic example of pandas_flow usage.

This example demonstrates how to track pandas operations
and generate a flowchart visualization.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

# Add parent directory to path for local development
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas_flow


def create_sample_data():
    """Create sample DataFrames for demonstration."""
    np.random.seed(42)

    # Patients data
    n_patients = 1000
    patients = pd.DataFrame(
        {
            "patient_id": range(1, n_patients + 1),
            "name": [f"Patient_{i}" for i in range(1, n_patients + 1)],
            "age": np.random.randint(5, 95, n_patients),
            "gender": np.random.choice(["M", "F"], n_patients),
            "city": np.random.choice(
                ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"], n_patients
            ),
        }
    )

    # Exams data (multiple exams per patient)
    n_exams = 3000
    exams = pd.DataFrame(
        {
            "exam_id": range(1, n_exams + 1),
            "patient_id": np.random.choice(range(1, n_patients + 1), n_exams),
            "exam_date": pd.date_range("2023-01-01", periods=n_exams, freq="h"),
            "exam_type": np.random.choice(
                ["Blood Test", "X-Ray", "MRI", "CT Scan", "Ultrasound"], n_exams
            ),
            "result_value": np.random.uniform(0, 100, n_exams),
            "status": np.random.choice(
                ["completed", "pending", "cancelled"], n_exams, p=[0.8, 0.15, 0.05]
            ),
        }
    )

    return patients, exams


def main():
    """Run the example pipeline."""
    print("=" * 60)
    print("pandas_flow Basic Example")
    print("=" * 60)
    print()

    # Setup the flow tracker
    flow = pandas_flow.setup(
        track_row_count=True,
        track_variables={
            "patient_id": "n_unique",
            "exam_type": "n_unique",
        },
        stats_variable="age",
        stats_types=["min", "max", "mean", "std", "histogram"],
        theme="default",
    )

    print("Creating sample data...")
    patients, exams = create_sample_data()

    # Register DataFrames with names (for better visualization)
    flow.register_dataframe(patients, name="patients", source_file="patients.csv")
    flow.register_dataframe(exams, name="exams", source_file="exams.csv")

    # Record initial load operations manually
    flow.record_operation(
        operation_type=pandas_flow.OperationType.READ_CSV,
        operation_name="Load Patients",
        input_dfs=[],
        output_df=patients,
        description="Load patient demographics",
        arguments={"file": "patients.csv"},
    )

    flow.record_operation(
        operation_type=pandas_flow.OperationType.READ_CSV,
        operation_name="Load Exams",
        input_dfs=[],
        output_df=exams,
        description="Load exam records",
        arguments={"file": "exams.csv"},
    )

    print("Processing data...")

    # Merge patients with exams
    combined = patients.merge(exams, on="patient_id", how="inner")

    # Filter completed exams only
    completed = combined.query("status == 'completed'")

    # Filter adults (age >= 18)
    adults = completed.query("age >= 18")

    # Remove duplicates
    unique_exams = adults.drop_duplicates(subset=["patient_id", "exam_date"])

    # Add calculated columns
    final = unique_exams.assign(
        age_group=pd.cut(
            unique_exams["age"],
            bins=[18, 30, 50, 70, 100],
            labels=["18-30", "31-50", "51-70", "71+"],
        ),
        year=unique_exams["exam_date"].dt.year,
    )

    # Sort by date
    final = final.sort_values("exam_date")

    # Drop unnecessary columns
    result = final.drop(columns=["name", "status"])

    print()
    print("Pipeline Summary:")
    print(flow.summary())

    # Render to multiple formats
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    # Markdown
    md_path = output_dir / "pipeline_flowchart.md"
    flow.render(str(md_path), title="Patient Exam Pipeline")
    print(f"✓ Markdown saved to: {md_path}")

    # HTML
    html_path = output_dir / "pipeline_flowchart.html"
    flow.render(str(html_path), title="Patient Exam Pipeline")
    print(f"✓ HTML saved to: {html_path}")

    # Raw Mermaid
    mmd_path = output_dir / "pipeline_flowchart.mmd"
    flow.render(str(mmd_path), title="Patient Exam Pipeline")
    print(f"✓ Mermaid saved to: {mmd_path}")

    print()
    print("Mermaid Code Preview:")
    print("-" * 40)
    mermaid_code = flow.get_mermaid(direction="TB", include_legend=True)
    print(mermaid_code[:2000])
    if len(mermaid_code) > 2000:
        print("... (truncated)")

    print()
    print("=" * 60)
    print("Example completed successfully!")
    print("=" * 60)

    return result


if __name__ == "__main__":
    main()
