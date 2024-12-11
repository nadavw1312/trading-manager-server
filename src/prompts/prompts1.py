import os


columns = """'Datetime', 'Open', 'High', 'Low', 'Close', 'Volume'"""
after_entry_columns = """entry_price (which mean the price we entered the position) entry_time (which mean the time we entered the position)"""
timeframes = """
     - Intraday: '1m', '5m', '15m', '30m', '60m','90m'
     - Higher timeframes: '1d', '5d', '1wk', '1mo', '3mo'
"""
categories = ["overlap studies","momentum","volume","volatility","price","cycle","pattern"]

calcs_docs = "additional doc files i sent you"

important_notes = """Important notes:
Your are senior python developer and senior data scientist and experienced trader profficient in creating conditions and calculations.
Also you understand human readability and simplicity, especially when naming.
Make sure everyting created as requested and ready to be used in production, all the list of params are created."""

calculation_alias = "SMA_<timeframe>_<window>"

using_lirbary_version = """Lookup Documentation: Always refer to the official Polars documentation for version 1 and Polars python version 1.9 to verify that the methods used are current and not deprecated.
Explicitly Avoid Deprecated Methods: Be vigilant in avoiding any methods that are marked as deprecated in the version specified.
Current stable methods: with_columns, cum_sum, group_by, etc...
""" 

def condition_prompt():
    return f"""
Conditions are trading conditions that use calculations to evaluate trading signals for entering or exiting positions but cant be used as both at the same time.
Each condition has a clear, singular purpose, either for entering a trade or for exiting a trade.
Create a Python Dictionary for a trading condition, which can use the available calculations in {calcs_docs}. If required calculations are not implemented, create them in a separate Python Dictionary.

The trading condition should be **logical** in design, utilizing **single timeframes** or combining **multiple timeframes** creatively.
When generating conditions, please use clear and consistent naming for functions and parameters.
**Naming Rules for `name`, `symbol`, and `identifiers`:**
- Do not use specific numeric values (e.g., "0.8", "14", "1d").
- Use dynamic names that represent the purpose of the condition or calculation (e.g., "AtrExit", "SmaCrossover", "AtrMultiplierCloseExit") instead of names like "atrExit5min".
- Do not include timeframes, numeric values, or multipliers in the names.
- Condition should be able to be used for all possibilities it can offer like crose above, cross below, greater than, less than, etc...
- Condition should have a clear purpose if there are more then 1 purpose make more then 1 condition.

**Structure:**
1. **name**: A descriptive and unique name for the condition,easy to understand and readable by humans.
2. **symbol**: A unique short symbol representing the condition.
3. **short_description**: A brief explanation of what the condition does and how it works with different parameter values.
4. **long_description**: An extended explanation of the condition's functionality and parameter effects.
5. **trader_usage_example**: An English description of how a trader might use the condition for a trading decision.
6. **programmer_usage_example**: An example of how to use the condition in code with full parameter examples (e.g., `SmaAboveEma['calc_pl'](dfs, params)`).
7. **is_only_exit**: A boolean indicating if the condition is used only for exit signals.
8. **actions**: Include all logical variations the condition supports (e.g., crosses_above, crosses_below, equals).
9. **logical_operators**: If present, capture logical connectors like "and", "or", "not".
Use standardized terms for actions and logical operators (e.g., crosses_above, greater_than, less_than, and, or, not).
10. **params**: A dictionary that includes keys with thier default value:
    required keys:
        **condition_timeframe**: The primary timeframe for evaluating the condition.
        **is_long**: A required boolean indicating if the condition is for a long (`true`) or short (`false`) position.
    optional keys:
        - If applicable, additional supporting timeframes (e.g., `trend_timeframe`, `atr_timeframe`) for multi-timeframe analysis.
        - Other dynamic parameters relevant to the condition (e.g., thresholds, indicator periods). **No hardcoded values**; all dynamic values should be configurable through the `params` dictionary.
11. **params_fields**: A dictionary where each key is a parameter from **params**, and the value is a dictionary with:
    - **type**: The expected data type (e.g., `int`, `float`, `string`, `boolean`, `list`).
    - **options** or **range**: Valid options or value ranges for the parameter.
    - **title**: A human-readable title.
    - **description**: An explanation of the parameter.
12. **calculations_params**: A dictionary where each key is a calculation from required_calculations, and the value is a dictionary with:
    - calculation_param_name: The name of the parameter in the calculation.
    - condition_param_name: The name of the parameter in the condition that maps to the calculation parameter.
13. **identifiers**: A list of unique and descriptive identifiers for the condition, e.g indicators, calculations.
14. **category**: The category of the condition (e.g., trend, volatility, momentum, volume).
15. **required_libraries**: A list of libraries that the condition uses and imports in the code (these will be installed to prepare the environment).
16. **required_calculations**: A list of calculations required by the condition.
17. **condition_logic**: provides a standardized expression of the condition's logic
18. **calc_pl**: A Python function written in string which mean Wrap the entire function in triple double quotes (implements logic on a regular `pl.DataFrame`):
        Include at the top: `import` relevant libraries, `import polars as pl`.
        - Refer to {calcs_docs} for available calculations..
        - Uses Polars data manipulation, consult Polars Docs with an emphasis on vectorized operations, use stable methods!!!.
        {using_lirbary_version}
        - **Parameters**:
        - `dfs`: A dictionary where each key is a timeframe, and each value is a DataFrame with columns {columns}. Only the condition timeframe can include {after_entry_columns} if used for exit.
        - `params`: The parameters for the condition, as structured above.
      - **Function Details**:
        - Execute required calculations dynamically using `globals().get('<calculation_class_name>')['calc_pl'](df, params)` and expect the result to be a `pl.DataFrame` with Datetime and the calculated columns like SMA_<timeframe>_<window>.
        - If different timeframes are used, merge them on the condition timeframe and fill missing values from the higher timeframe if needed.
        - **Unique Column Names**: Because we not know if there are cases where df contain the same column multiple times (e.g., two SMAs with different windows), ensure unique column names and append the parameter value and timeframe (e.g., `SMA_<timeframe>_<window>`).
        - **Adapt the logic** to handle both long and short positions as defined by `is_long`.
        - avoid nested f-string issue.
        - Generate alias for the condition with all params values used.
        - Return a `pl.Series` Boolean series indicating whether the condition is met.
        - Use try catch blocks to handle errors and add comments to the code.
        - Ensure the function is production-ready.

"""

calculation_returns_sturcture_instruction = """
ensure unique column names and append the parameter value and timeframe (e.g., `SMA_<timeframe>_<window>`).. Dont use hard coded values like 'MACD_1d_12_26' 
"""

def create_calculation():
    return f"""
Calculations are technical indicators or computations based on data columns that can be used in trading conditions to determine entering or exiting positions.
Create a new calculation Python Dictionary that defines a technical indicator or computation using the provided data columns. These calculations will be used within trading conditions for making entry or exit decisions.

**Important Notes:**
- **Avoid Duplication**: Only create a new calculation Python Dictionary if it doesn't already exist in {calcs_docs}.
- **Reusability**: If a required calculation is not implemented and is a generic calculation that can be usable in diffenet calculations, create it in a separate Python Dictionary following this structure.

**Structure:**

1. **symbol**: A unique, short symbol representing the calculation (e.g., `rsi`, `atr`).
2. **name**: A descriptive and unique name for the calculation.
3. **short_description**: A brief explanation of what the calculation does and how it works with different parameter values.
4. **long_description**: An extended explanation of the calculation's functionality and parameter effects.
5. **trader_usage_example**: An English description of how a trader might use the calculation for a trading decision.
6. **programmer_usage_example**: An example of how to use the calculation only without imports and without any other code,show full parameter usecase example (e.g., `atr['calc_pl'](df, params)`).
7. **returns_structure_of_calc_pl**: The return structure of the calculation calc_pl function, including:
    - **type**: The return type (e.g., `pl.DataFrame`).
    - **columns**: An array of dictionaries, each with:
        - **name**: The column name When defining column names use timeframe and parameter value (e.g., `SMA_<timeframe>_<window>`) is good but (e.g, SMA_1d_20) is bad, very important!!, if not implemented we risk columns with the same name.
        here the name must be dynamic without hardcoded values.
        - **dtype**: The data type of the column.(Polars data types)
8. **params**: A dictionary that includes:
    - **timeframe**: The primary timeframe for evaluating the calculation(e.g., 5m, 1d).
    - **Dynamic parameters** relevant to the calculation (e.g., thresholds, periods). Naming should be generic.
    - **No Hardcoded Values** All dynamic values (such as window, threshold) should be configurable through this dictionary.
    - **Default Values** Assign default values to each parameter key.
9. **params_fields**: A dictionary where each key is a parameter, and the value is a dictionary with:
    - **type**: Expected data type (e.g., `"int"`, `"float"`).
    - **range**: An array with two values representing the minimum and maximum.
    - **title**: A human-readable title.
    - **description**: Explanation of the parameter.
10. **identifiers**: A list of unique and descriptive identifiers for the calculation , such as used name, symbol, and related calculations.
11. **category**: The category of the calculation (e.g., trend, volatility, momentum, volume).
12. **required_libraries**: A list of libraries that the calculation uses and imports in the code(e.g., 'polars') (these will be installed to prepare the environment).
13. **required_calculations**: A list of other calculations that this one depends on (e.g., `sma`, `rsi`, `atr`, `cci`, `ema`).
14. **plot_type**: Defines the type of chart to plot for this calculation (e.g., `'line'`, `'area'`, `'candlestick'`, `'bar'`, `'histogram'`).
15. **plot_on**: Defines where the plot should be rendered (`'candlestick'` for overlay or `'separate_pane'` for a separate pane).
16. **plot_data_format**: A dictionary including:
    - **time_field**: The field containing the timestamp for the x-axis (e.g., `'Datetime'`).
    - **value_field**: The field containing the calculated value to be plotted array containing the column names (e.g., `['SMA_<timeframe>_<window>']`), the name must be dynamic without hardcoded values.
17. **calc_pl**: A Python valid **function** written in string which mean Wrap the entire function in triple double quotes (implements logic on a regular `pl.DataFrame`):
        - Only show the formatted code itself, without additional Markdown or language indicators that disrupt readability.
        - Refer to {calcs_docs} for available calculations.
        if not implement the calculation, if any an other calculation is required use it like sescribed `globals().get('<symbol>')['['calc_pl'](df, params)`
        - Uses Polars data manipulation https://docs.pola.rs/api/python/dev/reference/dataframe/index.html, consult Polars Docs with an emphasis on vectorized operations for efficiency,use stable methods!!!.
        {using_lirbary_version}
    )
        - **Parameters**:
            - `df`: A `pl.DataFrame` with columns {columns}.
            - `params`: The parameters for the calculation.
        - **Function Details**:
            - Dont add any comments for Args and Returns and dont add try-catch blocks.
            - Include at the top: `import` relevant libraries, `import polars as pl`..
            Other used calculations will be available via `globals().get('<calculation_symbol>')`.
            - **Avoid Overwriting**: Do not overwrite existing columns when performing new calculations on the same DataFrame, use alias with timeframe and parameter value.
            - use alias with logical naming to avoid multiple expressions are returning the same default column.
            - If any required calculation (such as SMA, EMA, etc.) already exists, reuse it dynamically using `globals().get('<symbol>')['calc_pl'](df, params)` and alias the result how you want.
            - Avoid nested f-string issue.
            - The function should use efficient DataFrame operations, with minimal redundant steps or intermediate variables unless they significantly enhance readability. Avoid creating variables for intermediate results if calculations can be directly applied using with_columns or similar methods in Polars, keeping the code concise yet clear.
            - **Column References**: Only use `pl.col("column_name")` with actual column names, and avoid passing expressions directly to functions that expect column names. Use `pl.max_horizontal()` or `pl.min_horizontal()` for comparisons across multiple expressions.
            - **Separate `.with_columns()` for Steps**: Use distinct `.with_columns()` calls for multi-step calculations, applying final calculations (e.g., `rolling_mean`, `rolling_std`) only after intermediate columns are calculated.
            - **Dynamic Aliases**: Always use formatted strings to dynamically name output columns with timeframe and parameter values, avoiding hardcoded column names.
            - **Error-Free Aggregations**: Avoid `pl.col()` or other Polars functions directly on expressions. If a calculation requires a maximum or minimum across expressions, use functions like `pl.max_horizontal()`.
            - **Return Structure**: The function should return a `pl.DataFrame` containing only the newly calculated columns and Datetime with .select() method at the end of each function.(we working on Dataframe)
            - Use try catch blocks to handle errors and add comments to the code.
"""

with open("docs/conditions.txt", 'w') as file:
        file.write(condition_prompt())
with open("docs/calculations.txt", 'w') as file:
        file.write(create_calculation())