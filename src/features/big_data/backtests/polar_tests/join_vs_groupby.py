import polars as pl
import numpy as np
import datetime

from common.utils.timer import Timer

def test_group_by_vs_join_asof():
    # Set random seed for reproducibility
    np.random.seed(0)

    # Generate large datasets with timestamps
    n = 1_000_000  # Number of rows

    # Generating timestamps and groups for transactions
    timestamps = [datetime.datetime(2023, 1, 1) + datetime.timedelta(minutes=i) for i in range(n)]
    groups = np.random.choice(['A', 'B', 'C', 'D'], size=n)
    values = np.random.randint(1, 1000, size=n)

    df_transactions = pl.DataFrame({
        "timestamp": timestamps,
        "group": groups,
        "value": values
    })

    # Generating timestamps and groups for reference data with fewer rows
    ref_timestamps = [datetime.datetime(2023, 1, 1) + datetime.timedelta(minutes=i*5) for i in range(n // 10)]
    ref_groups = np.random.choice(['A', 'B', 'C', 'D'], size=n // 10)
    ref_values = np.random.randint(1, 1000, size=n // 10)

    df_reference = pl.DataFrame({
        "timestamp": ref_timestamps,
        "group": ref_groups,
        "ref_value": ref_values
    })

    with Timer("--------group_by --------") as t:
        # 1. Using group_by to aggregate data (e.g., calculating mean value per group)
        grouped_df = df_transactions.group_by("group").agg([
            pl.col("value").mean().alias("average_value")
        ])

    with Timer("--------join_asof --------") as t:
        # 2. Using join_asof to find the closest preceding reference values based on timestamp within each group
        joined_df = df_transactions.join_asof(
            df_reference,
            on="timestamp",
            by="group",
            strategy="backward"
        )


    # # Display results
    # print("Grouped DataFrame (group_by):")
    # print(grouped_df)

    # print("\nJoined DataFrame (join_asof):")
    # print(joined_df)
