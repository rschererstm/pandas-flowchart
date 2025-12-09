#!/usr/bin/env python3
"""
pandas-flowchart - Track pandas operations and generate Mermaid flowcharts.

This is the main entry point for running demos and examples.
"""

import pandas as pd
import numpy as np
from pathlib import Path

import pandas_flow


def quick_demo():
    """
    Quick demonstration of pandas_flow capabilities.
    
    This function creates sample data and demonstrates the core
    features of the library.
    """
    print("=" * 60)
    print("pandas_flow Quick Demo")
    print("=" * 60)
    print()
    
    # Setup the tracker
    flow = pandas_flow.setup(
        track_row_count=True,
        track_variables={
            "user_id": "n_unique",
            "category": "n_unique",
        },
        stats_variable="amount",
        stats_types=["min", "max", "mean", "std", "histogram"],
    )
    
    # Create sample data
    np.random.seed(42)
    n = 1000
    
    # Users DataFrame
    users = pd.DataFrame({
        "user_id": range(1, 501),
        "name": [f"User_{i}" for i in range(1, 501)],
        "age": np.random.randint(18, 80, 500),
        "country": np.random.choice(["USA", "UK", "Germany", "France", "Japan"], 500),
    })
    
    # Transactions DataFrame
    transactions = pd.DataFrame({
        "tx_id": range(1, n + 1),
        "user_id": np.random.choice(range(1, 501), n),
        "amount": np.random.exponential(100, n).round(2),
        "category": np.random.choice(["Electronics", "Clothing", "Food", "Books", "Other"], n),
        "date": pd.date_range("2024-01-01", periods=n, freq="h"),
        "status": np.random.choice(["completed", "pending", "failed"], n, p=[0.85, 0.10, 0.05]),
    })
    
    # Register source DataFrames
    flow.register_dataframe(users, name="users", source_file="users.csv")
    flow.register_dataframe(transactions, name="transactions", source_file="transactions.csv")
    
    # Record initial loads
    flow.record_operation(
        operation_type=pandas_flow.OperationType.READ_CSV,
        operation_name="Load Users",
        input_dfs=[],
        output_df=users,
        description="Load user data",
        arguments={"file": "users.csv"},
    )
    
    flow.record_operation(
        operation_type=pandas_flow.OperationType.READ_CSV,
        operation_name="Load Transactions",
        input_dfs=[],
        output_df=transactions,
        description="Load transaction data",
        arguments={"file": "transactions.csv"},
    )
    
    print("Step 1: Loaded sample data")
    print(f"  - Users: {len(users)} rows")
    print(f"  - Transactions: {len(transactions)} rows")
    print()
    
    # Join users with transactions
    print("Step 2: Joining users with transactions...")
    combined = users.merge(transactions, on="user_id", how="inner")
    print(f"  → Combined: {len(combined)} rows")
    
    # Filter completed transactions
    print("Step 3: Filtering completed transactions...")
    completed = combined.query("status == 'completed'")
    print(f"  → Completed: {len(completed)} rows")
    
    # Filter high-value transactions
    print("Step 4: Filtering high-value transactions (amount > 50)...")
    high_value = completed.query("amount > 50")
    print(f"  → High value: {len(high_value)} rows")
    
    # Add calculated columns
    print("Step 5: Adding calculated columns...")
    enriched = high_value.assign(
        age_group=pd.cut(high_value["age"], bins=[18, 30, 50, 80], labels=["Young", "Middle", "Senior"]),
        month=high_value["date"].dt.month,
    )
    
    # Remove duplicates
    print("Step 6: Removing duplicates...")
    unique = enriched.drop_duplicates(subset=["user_id", "date"])
    print(f"  → Unique: {len(unique)} rows")
    
    # Sort by amount
    print("Step 7: Sorting by amount...")
    sorted_df = unique.sort_values("amount", ascending=False)
    
    # Drop temporary columns
    print("Step 8: Dropping status column...")
    final = sorted_df.drop(columns=["status"])
    
    print()
    print("Pipeline completed!")
    print()
    
    # Print summary
    print(flow.summary())
    
    # Generate outputs
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    # Save Markdown
    md_path = output_dir / "demo_flowchart.md"
    flow.render(str(md_path), title="Transaction Analysis Pipeline")
    print(f"✓ Markdown flowchart saved to: {md_path}")
    
    # Save HTML
    html_path = output_dir / "demo_flowchart.html"
    flow.render(str(html_path), title="Transaction Analysis Pipeline")
    print(f"✓ HTML flowchart saved to: {html_path}")
    
    # Print Mermaid preview
    print()
    print("Mermaid Code Preview:")
    print("-" * 40)
    mermaid = flow.get_mermaid(direction="TB")
    # Print first portion
    lines = mermaid.split("\n")
    for line in lines[:30]:
        print(line)
    if len(lines) > 30:
        print(f"... ({len(lines) - 30} more lines)")
    
    print()
    print("=" * 60)
    print("Demo completed! Check the 'output' folder for generated files.")
    print("=" * 60)
    
    return final


def main():
    """Main entry point."""
    quick_demo()


if __name__ == "__main__":
    main()
