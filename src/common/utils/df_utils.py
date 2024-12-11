import polars as pl
from typing import Dict

def convert_dfs_to_lazyframes(dfs: Dict[str, pl.DataFrame]) -> Dict[str, pl.LazyFrame]:
    """
    Converts all DataFrames in the `dfs` dictionary to LazyFrames.
    
    Args:
        dfs: Dictionary of DataFrames to be converted.
    
    Returns:
        A dictionary where the DataFrames have been converted to LazyFrames.
    """
    lazy_dfs = {key: df.lazy() for key, df in dfs.items()}
    return lazy_dfs