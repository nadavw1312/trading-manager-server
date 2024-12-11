import os


columns = """'Datetime', 'Open', 'High', 'Low', 'Close', 'Volume'"""
after_entry_columns = """entry_price (which mean the price we entered the position), enttry_datetime (which mean the datetime we entered the position), entry_Low"""
timeframes = """
     - Intraday: '1m', '5m', '15m', '30m', '60m','90m'
     - Higher timeframes: '1d', '5d', '1wk', '1mo', '3mo'
"""


calcs_docs = "additional doc files i sent you"

important_notes = """Important notes:
Your are senior python developer and senior data scientist and experienced trader profficient in creating conditions and calculations.
Also you understand human readability and simplicity, especially when naming.
Make sure everyting created as requested and ready to be used in production, all the list of params are created."""


def add_after_entry_calc_params():
      return f"""If used for exit, the following adiitonal columns ban be used: {after_entry_columns}""" 


def using_lirbary_version_prompt(name:str = "Polars", polar_version:str="1", polar_python_version:str = "1.9.0"):
      return f"""Double-Check the Documentation: Always refer to the official {name} documentation for version {polar_version} and {name} python version {polar_python_version} to verify that the methods used are current and not deprecated.
Explicitly Avoid Deprecated Methods: Be vigilant in avoiding any methods that are marked as deprecated in the version specified.
Current stable methods: with_columns, cum_sum, group_by, etc...
""" 

def condition_prompt():
    return f"""
Conditions are trading conditions that use calculations to evaluate trading signals for entering or exiting positions.
Create a Python Dictionary for a trading condition.

The trading condition should be **logical** in design, utilizing **single timeframes** or combining **multiple timeframes** creatively.

**Naming Rules for `name`, `symbol`, `class_name`, and `identifiers`:**
- Do not use specific numeric values (e.g., "0.8", "14", "1d").
- Use dynamic names that represent the purpose of the condition or calculation (e.g., "AtrExit", "SmaCrossover", "AtrMultiplierCloseExit") instead of names like "atrExit5min".
- Do not include timeframes, numeric values, or multipliers in the names.

**Structure:**
1. **name**: A descriptive and unique name for the condition,easy to understand and readable by humans.
2. **symbol**: A unique short symbol representing the condition.
3. **class_name**: The `symbol` in CamelCase.
4. **short_description**: A brief explanation of what the condition does and how it works with different parameter values.
5. **long_description**: An extended explanation of the condition's functionality and parameter effects.
6. **trader_usage_example**: An English description of how a trader might use the condition for a trading decision.
7. **programmer_usage_example**: An example of how to use the condition in code with full parameter examples (e.g., `SmaAboveEma.calc(dfs, params)`).
8. **is_only_exit**: A boolean indicating if the condition is used only for exit signals.
9. **actions**: A list of possible actions (e.g., "cross above", "greater than", "less than")
10. **logical_operators**: If present, capture logical connectors like "and", "or", "not".
11. **params**: A dictionary that includes keys with thier default value:
    required keys:
        **condition_timeframe**: The primary timeframe for evaluating the condition.
        **is_long**: A required boolean indicating if the condition is for a long (`true`) or short (`false`) position.
    optional keys:
        - If applicable, additional supporting timeframes (e.g., `trend_timeframe`, `atr_timeframe`) for multi-timeframe analysis.
        - Other dynamic parameters relevant to the condition (e.g., thresholds, indicator periods). **No hardcoded values**; all dynamic values should be configurable through the `params` dictionary.
12. **params_fields**: A dictionary where each key is a parameter from **params**, and the value is a dictionary with:
    - **type**: The expected data type (e.g., `int`, `float`, `string`, `boolean`, `list`).
    - **options** or **range**: Valid options or value ranges for the parameter.
    - **title**: A human-readable title.
    - **description**: An explanation of the parameter.
13. **identifiers**: A list of unique and descriptive identifiers for the condition, such as used columns and indicators.
14. **category**: The category of the condition (e.g., trend, volatility, momentum, volume).
15. **required_libraries**: A list of libraries that the condition uses and imports in the code (these will be installed to prepare the environment).
16. **required_calculations**: A list of calculations required by the condition.
17. **used_columns**: A list of data columns used by the condition.
18. **class_def**: A Python class named after `class_name`, provided as a string. Ensure it contains `calc` function:
        Include at the top: `import` relevant libraries, `import polars as pl`.
    - **calc**: (implements logic on a regular `pl.DataFrame`):
      - Uses Polars data manipulation; consult Polars Docs with an emphasis on vectorized operations.
      {using_lirbary_version_prompt()}
      - **Parameters**:
        - `dfs`: A dictionary where each key is a timeframe, and each value is a DataFrame with columns {columns}. Only the condition timeframe can include {add_after_entry_calc_params()}.
        - `params`: The parameters for the condition, as structured above.
      - **Function Details**:
        - implements logic 
        - If different timeframes are used, merge them on the condition timeframe and fill missing values from the higher timeframe if needed.
        - **Unique Column Names**: If applying the same calculation multiple times (e.g., two SMAs with different windows), ensure unique column names and append the parameter value and timeframe (e.g., `SMA_<timeframe>_<window>`).
        - **Adapt the logic** to handle both long and short positions as defined by `is_long`.
        - avoid nested f-string issue.
        - Return a `pl.Series` Boolean series indicating whether the condition is met.
        - Ensure the function is production-ready.
        - Dont add any comments for Args and Returns and dont add try-catch blocks.
"""



with open("docs/conditions_cond.txt", 'w') as file:
        file.write(condition_prompt())
