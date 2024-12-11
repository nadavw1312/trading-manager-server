import os


columns = """'Datetime', 'Open', 'High', 'Low', 'Close', 'Volume'"""
after_entry_columns = """entry_price (which mean the price we entered the position), enttry_datetime (which mean the datetime we entered the position)"""
timeframes = """
     - Intraday: '1m', '5m', '15m', '30m', '60m','90m'
     - Higher timeframes: '1d', '5d', '1wk', '1mo', '3mo'
"""


calcs_docs = "additional doc files i sent you"

important_notes = """Important notes:
Your are senior python developer and senior data scientist and experienced trader profficient in creating conditions and calculations.
Also you understand human readability and simplicity, especially when naming.
Catch and raise any errors that occur during the execution of the function and add relevant comments.
Make sure everyting created as requested and ready to be used in production, all the list of params are created."""


def add_after_entry_calc_params():
      return f"""If used for exit, the following adiitonal columns ban be used: entry_price (which mean the price we entered the position), enttry_datetime (which mean the datetime we entered the position)""" 


def using_lirbary_version_prompt(name:str = "Polars", polar_version:str="1", polar_python_version:str = "1.9.0"):
      return f"""Double-Check the Documentation: Always refer to the official {name} documentation for version {polar_version} and {name} python version {polar_python_version} to verify that the methods used are current and not deprecated.
Explicitly Avoid Deprecated Methods: Be vigilant in avoiding any methods that are marked as deprecated in the version specified.
Current stable methods: with_columns,cum_sum,group_by, etc...
""" 

def condition_prompt():
    return f"""
Conditions are trading conditions that use calculations to evaluate trading signals for entering or exiting positions.
Create a JSON for a trading condition, which can use the available calculations in {calcs_docs}. If required calculations are not implemented, create them in a separate JSON.

The trading condition should be **logical** in design, utilizing **single timeframes** or combining **multiple timeframes** creatively.

**Naming Rules for `name`, `symbol`, `class_name`, and `identifiers`:**
- Do not use specific numeric values (e.g., "0.8", "14", "1d").
- Use dynamic names that represent the purpose of the condition or calculation (e.g., "AtrExit", "SmaCrossover", "AtrMultiplierCloseExit") instead of names like "atrExit5min".
- Do not include timeframes, numeric values, or multipliers in the names.

**Structure:**
1. **name**: A descriptive and unique name for the condition, readable by humans (e.g., based on indicators, price patterns, volume behaviors, or other market factors).
2. **symbol**: A unique short symbol representing the condition.
3. **class_name**: The `symbol` in CamelCase.
4. **short_description**: A brief explanation of what the condition does and how it works with different parameter values.
5. **long_description**: An extended explanation of the condition's functionality and parameter effects.
6. **trader_usage_example**: An English description of how a trader might use the condition for a trading decision.
7. **programmer_usage_example**: An example of how to use the condition in code with full parameter examples (e.g., `SmaAboveEma.calc(dfs, params)`).
8. **is_only_exit**: A boolean indicating if the condition is used only for exit signals.
9. **params**: A dictionary that includes:
   - **condition_timeframe**: The primary timeframe for evaluating the condition. Timeframes can include:
     {timeframes}
   - **is_long**: A required boolean indicating if the condition is for a long (`true`) or short (`false`) position.
   - If applicable, additional supporting timeframes (e.g., `trend_timeframe`, `atr_timeframe`) for multi-timeframe analysis.
   - Other dynamic parameters relevant to the condition (e.g., thresholds, indicator periods). **No hardcoded values**; all dynamic values should be configurable through the `params` dictionary.
10. **params_fields**: A dictionary where each key is a parameter, and the value is a dict with:
    - **type**: The expected data type (e.g., `int`, `float`, `string`, `boolean`, `list`).
    - **options** or **range**: Valid options or value ranges for the parameter.
    - **title**: A human-readable title.
    - **description**: An explanation of the parameter.
11. **identifiers**: A list of unique and descriptive identifiers for the condition, such as used columns and indicators.
12. **category**: The category of the condition (e.g., trend, volatility, momentum, volume).
13. **required_libraries**: A list of libraries that the condition uses and imports in the code (these will be installed to prepare the environment).
14. **required_calculations**: A list of calculations required by the condition.
15. **used_columns**: A list of data columns used by the condition.
16. **calc**: A Python function(implement condition logic):
      - Uses Polars data manipulation; consult Polars Docs with an emphasis on vectorized operations.
      - Refer to {calcs_docs} for available calculations.
      {using_lirbary_version_prompt()}
      - **Parameters**:
        - `dfs`: A dictionary where each key is a timeframe, and each value is a DataFrame with columns {columns}. Only the condition timeframe can include {add_after_entry_calc_params()}.
        - `params`: The parameters for the condition, as structured above in **params**.
      - **Function Details**:
        - Include at the top: `import` relevant libraries, `import polars as pl`. Other used calculations will be available via `locals().get('<calculation_class_name>')`.
        - Execute required calculations dynamically using `locals().get('<calculation_class_name>').calc(df, params)`.
        - If different timeframes are used, merge them on the condition timeframe by Datetime and fill missing values from the higher timeframe.
        - **Unique Column Names**: If applying the same calculation multiple times (e.g., two SMAs with different windows),or there is a chance other condition created similar column, ensure unique column names and append the parameter value and timeframe (e.g., `SMA_<timeframe>_<window>`).
        - **Avoid Overwriting**: Do not overwrite existing columns when performing new calculations on the same DataFrame,.
        - Adapt the logic to handle both long and short positions as defined by `is_long`.
        - Return a `pl.Series` Boolean series indicating whether the condition is met.
        - Catch and raise any errors that occur during execution.
        - Ensure the function is production-ready.
17. **calc_lazy**: Similar to `calc` but:
      - **Input Handling**: Accepts either a DataFrame or a LazyFrame. If it's a DataFrame, convert it to a LazyFrame.
      - Do not collect the result on the DataFrame.
      - Return the LazyFrame with the new column added.
18. **test_class_def**: A Python script as a string containing three functions:
    - **create_test_df**: Creates and returns `test_df` and `expected_result_df`.
    - **test_calc**: Tests the logic of the condition using `calc`:
      - Include at the top: `import` relevant libraries, `import polars as pl`.
      - Use `create_test_df`.
      - Run the condition on `test_df` with relevant `params`.
      - Compare the result with `expected_result_df` using `assert`.
19. **test_calc_lazy**: Similar to `test_calc` but tests `calc_lazy`.

**Important Notes:**
- If a required calculation is not implemented and is a generic calculation usable in multiple conditions, create it in a separate JSON following the calculation generation structure.
"""

def create_calculation():
    return f"""
Calculations are technical indicators or computations based on data columns that can be used in trading conditions to determine entering or exiting positions.

Create a new calculation JSON that defines a technical indicator or computation using the provided data columns. These calculations will be used within trading conditions for making entry or exit decisions.

**Important Notes:**
- **Avoid Duplication**: Only create a new calculation JSON if it doesn't already exist in {calcs_docs}. Use existing calculations directly without recreating them.
- **Reusability**: If a required calculation is not implemented and is a generic calculation usable in multiple conditions, create it in a separate JSON following this structure.

**Structure:**

1. **symbol**: A unique, short symbol representing the calculation (e.g., `rsi`, `atr`).
2. **class_name**: CamelCase version of the symbol (e.g., `Rsi`, `Atr`).
3. **name**: A descriptive and unique name for the calculation.
4. **short_description**: A brief explanation of what the calculation does and how it works with different parameter values.
5. **long_description**: An extended explanation of the calculation's functionality and parameter effects.
6. **trader_usage_example**: An English description of how a trader might use the calculation for a trading decision.
7. **programmer_usage_example**: An example of how to use the calculation in code with full parameter examples (e.g., `Atr.calc(df, params)`).
8. **returns_structure**: The return structure of the calculation, including:
    - **type**: The return type (e.g., `pl.DataFrame`).
    - **columns**: An array of dictionaries, each with:
        - **name**: The column name.When defining column names, use placeholders (like <timeframe>, <fast_period>, <slow_period>, <signal_period>) instead of hardcoded values. For instance, use "MACD_<timeframe>_<fast_period>_<slow_period>" instead of "MACD_1d_12_26
        - **dtype**: The data type of the column.
9. **params**: A dictionary that includes:
    - **timeframe**: The primary timeframe for evaluating the calculation(e.g., 5m, 1d).
    - **Dynamic parameters** relevant to the calculation (e.g., thresholds, periods). Naming should be generic.
    - **No Hardcoded Values** All dynamic values (such as window, threshold) should be configurable through this dictionary.
    - **Default Values** Assign default values to each parameter key.
10. **params_fields**: A dictionary where each key is a parameter, and the value is a dict with:
    - **type**: Expected data type (e.g., `"int"`, `"float"`).
    - **range**: An array with two values representing the minimum and maximum.
    - **title**: A human-readable title.
    - **description**: Explanation of the parameter.
11. **identifiers**: A list of unique and descriptive identifiers for the calculation, such as used columns, name, and related indicators including the symbol.
12. **category**: The category of the calculation (e.g., trend, volatility, momentum, volume).
13. **required_libraries**: A list of libraries that the calculation uses and imports in the code (these will be installed to prepare the environment).
14. **required_calculations**: A list of other calculations that this one depends on.
15. **plot_type**: Defines the type of chart to plot for this calculation (e.g., `'line'`, `'area'`, `'candlestick'`, `'bar'`, `'histogram'`).
16. **plot_on**: Defines where the plot should be rendered (`'candlestick'` for overlay or `'separate_pane'` for a separate pane).
17. **plot_data_format**: A dictionary including:
    - **time_field**: The field containing the timestamp for the x-axis (e.g., `'Datetime'`).
    - **value_field**: The field containing the calculated value to be plotted (e.g., `'SMA_<window>'`).
18. **calc** (implements logic on a regular `pl.DataFrame`):
        - Refer to {calcs_docs} for available calculations.
        - Uses Polars data manipulation; consult Polars Docs with an emphasis on vectorized operations for efficiency.
        {using_lirbary_version_prompt()}
        - **Parameters**:
            - `df`: A `pl.DataFrame` with columns {columns}.
            - `params`: The parameters for the calculation like described in **params**.
        - **Function Details**:
            - Include at the top: `import` relevant libraries, `import polars as pl`. Other used calculations will be available via `locals().get('<calculation_class_name>')`.
            - **Unique Column Names**: If applying the same calculation multiple times (e.g., two SMAs with different windows), ensure unique column names and append the parameter value and timeframe (e.g., `SMA_<timeframe>_<window>`).
            - **Avoid Overwriting**: Do not overwrite existing columns when performing new calculations on the same DataFrame.
            - If any required calculation (such as SMA, EMA) already exists, reuse it dynamically using `locals().get('<class_name>').calc(df, params)`.
            - The function should return a `pl.DataFrame` result.
            - **Error Handling**: Include try-except blocks with meaningful error messages, raising a `ValueError` if necessary.
19. **calc_lazy**: Similar to `calc` but:
        - **Input Handling**: Accepts either a DataFrame or a LazyFrame. If it's a DataFrame, convert it to a LazyFrame.
        - Do not collect the result on the DataFrame.
        - Return the LazyFrame with the new column added.
20. **create_test_df**:python function Creates and returns `test_df` and `expected_result_df`.
21. **test_calc**: A Python function Tests the logic of the calculation using `calc` get **create_test_df** values as params:
        - Include at the top: `import` relevant libraries, `import polars as pl`.
        - Run the calculation on `test_df` with relevant `params`.
        - Compare the result with `expected_result_df` using `assert`.
22. **test_calc_lazy**: Similar to `test_calc` but tests `calc_lazy`.
"""

# print(create_condition_ands_calculations(is_entry=True))

with open("docs/conditions2.txt", 'w') as file:
        file.write(condition_prompt())
with open("docs/calculations2.txt", 'w') as file:
        file.write(create_calculation())