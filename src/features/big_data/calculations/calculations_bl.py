import importlib
import json
import logging
import os
from typing import Any
import polars as pl
import polars_talib as plta



from common.base.base_mongo_bl import BaseMongoBl
from common.services.models.calculations_model import CalculationsModel
from features.big_data.calculations.calculations_dal import CalculationsDal
from features.big_data.calculations.calculations_documenter import CalculationsDocumenter
from server.src.common.third_party_api.openai_api import OpenAIAssistant
from server.src.common.utils.singleton import singleton
from server.src.prompts import prompts1


@singleton
class CalculationsBl(BaseMongoBl[CalculationsDal, CalculationsModel]):
    def __init__(self):
        super().__init__(CalculationsDal)
        self.documenter = CalculationsDocumenter()  # For generating documentation
        self.compiled_calculations:dict[str, Any] = {}  # To store compiled calculations
        self.assistant = OpenAIAssistant(vector_store_name="calculations_vector_store", assistant_name="calculations_assistant", instructions=f"You are an expert in python programming and data analysis especially using python polars library. Every time you are asked to create a calculation follow the instructions: {prompts1.create_calculation()}")
        self.execution_namespace = {
            '__builtins__': __builtins__,
            'pl': pl,
            'plta': plta,
            # Include necessary libraries in the execution environment
        }
        
    
    def document_calculations(self):
        calculations = self.dal.get_all_calculations()
        return self.documenter.generate_documentation(calculations)
    
    def get_calculations(self):
        return self.dal.get_all_calculations()

    def add_calculation(self, calc_data: dict[str, Any]):
        """
        Adds a new calculation to the database and compiles it for execution.
        """
        try:
            # Validate the calculation data
            new_calculation = CalculationsModel(**calc_data)
            # Save the calculation to MongoDB
            self.dal.insert_one(new_calculation.model_dump(by_alias=True))
            return {"status": "success", "message": "Calculation added and compiled."}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_calculation_as_compiled_class(self, calc_doc: CalculationsModel) -> dict[str, Any] :
        """
        Compiles the class definition and adds it to the namespace for execution.
        """
        calc_pl = calc_doc.calc_pl
        if not calc_pl:
            raise ValueError("No calc_pl found in the calculation data.")

        symbol = calc_doc.symbol
        if symbol in self.compiled_calculations:
            return self.execution_namespace[symbol]

        # Compile required calculations first
        required_calculations = calc_doc.required_calculations
        for required_symbol in required_calculations:
            required_calc_doc = self.dal.get_calculation_by_symbol(required_symbol.lower())
            self.get_calculation_as_compiled_class(required_calc_doc)  # Recursive compilation of dependencies

        # Create temporary namespace for compilation
        temp_namespace = {}
        
        # Compile and execute the calculation code
        code_obj = compile(calc_pl, f"<calculation {symbol}>", 'exec')
        exec(code_obj, {**self.execution_namespace}, temp_namespace)
                
        self.compiled_calculations[symbol] = temp_namespace
        self.execution_namespace[symbol] = temp_namespace

        return self.execution_namespace[symbol]

    def update_calculation(self, symbol: str, update_data: dict[str, Any]):
        """
        Updates an existing calculation by its symbol.
        """
        try:
            self.dal.update_calculation(symbol, update_data)
            return {"status": "success", "message": "Calculation updated."}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def delete_calculation(self, symbol: str):
        """
        Deletes a calculation from the database.
        """
        try:
            self.dal.delete_calculation(symbol)
            return {"status": "success", "message": "Calculation deleted."}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def generate_documentation(self):
        """
        Generates and saves documentation for all calculations in the system.
        """
        try:
            calculations = self.dal.get_all_calculations()
            self.documenter.generate_documentation(calculations)
            return {"status": "success", "message": "Documentation generated."}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def snake_to_camel(self,data:dict):
        """
        Transforms a snake_case string to camelCase.
        """
        new_json = {}
        for snake_str in data:
            
            components = snake_str.split('_')
            new_json[components[0] + ''.join(x.title() for x in components[1:])] = data[snake_str]
        return new_json
    def load_python_file(self, file_path):
        # Load a Python file as a module and return its dictionary content
        spec = importlib.util.spec_from_file_location("module.name", file_path) #type:ignore
        module = importlib.util.module_from_spec(spec) #type:ignore
        spec.loader.exec_module(module)
        
        # Assume the Python file has a top-level dictionary named `data_dict`
        if hasattr(module, 'data_dict') and isinstance(module.data_dict, dict):
            return module.data_dict
        else:
            raise ValueError("Python file does not contain a valid dictionary named 'data_dict'")
    
    def load_and_insert_calculations(self):
        json_folder = "src/features/big_data/calculations/jsons"
        
        # Iterate over all files in the folder
        for file in os.listdir(json_folder):
            file_path = os.path.join(json_folder, file)
            
            # Process JSON files
            if file.endswith('.json'):
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    logging.info(f"Loaded JSON file: {file}")
                    
                    # Insert data into the database
                    self.dal.insert_one(self.snake_to_camel(data))
                    logging.info(f"Inserted data from {file} into the database.")
                
                except json.JSONDecodeError:
                    logging.error(f"Failed to parse JSON file: {file}")
                except Exception as e:
                    logging.error(f"Error inserting data from {file}: {e}")
            
            # Process Python files with dictionaries
            elif file.endswith('.py'):
                try:
                    data = self.load_python_file(file_path)
                    logging.info(f"Loaded Python file: {file}")
                    
                    # Insert data into the database
                    self.dal.insert_one(self.snake_to_camel(data))
                    logging.info(f"Inserted data from {file} into the database.")
                
                except Exception as e:
                    logging.error(f"Error loading or inserting data from {file}: {e}")

    
    def add_calculation_to_df(self, df:pl.DataFrame, calculation_symbol:str,calculation_params:dict[str,Any]):
        calc = self.dal.get_calculation_by_symbol(calculation_symbol)
        obj = self.get_calculation_as_compiled_class(calc)
        params = {**calc.params,**calculation_params}
        df_with_calc:pl.DataFrame = obj["calc_pl"](df, params)
        
        
        return df_with_calc
    
    def get_all_symbols(self):
        return self.dal.get_all_symbols()
