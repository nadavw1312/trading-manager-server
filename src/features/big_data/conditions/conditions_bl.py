import importlib

import json
import logging
import os
from typing import Any, Dict, List
import polars as pl
from pymongo.client_session import ClientSession


from common.base.base_mongo_bl import BaseMongoBl
from common.services.models.conditions_model import ConditionsModel
from features.big_data.calculations.calculations_bl import CalculationsBl
from features.big_data.conditions.conditions_dal import ConditionsDal
from features.big_data.conditions.conditions_documenter import ConditionsDocumenter
from server.src.common.services.models.calculations_model import CompiledCalc
from server.src.common.third_party_api.openai_api import OpenAIAPI, OpenAIAssistant
from server.src.common.utils.singleton import singleton
from server.src.features.big_data.validate_generated_script import validate_generated_script
from server.src.prompts import prompts1



@singleton
class ConditionsBl(BaseMongoBl[ConditionsDal, ConditionsModel]): 
    def __init__(self):
        super().__init__(ConditionsDal) # Data Access Layer for Conditions
        self.documenter = ConditionsDocumenter()  # For generating documentation
        self.compiled_conditions = {}  # To store compiled conditions
        self.compiled_calculations = {}  # To store compiled conditions
        self.assistant = OpenAIAssistant(vector_store_name="conditions_vector_store", assistant_name="conditions_assistant", instructions=f"You are an expert in python programming and data analysis especially using python polars library. Every time you are asked to create a condition follow the instructions: {prompts1.condition_prompt()}")
        self.execution_namespace = {
            '__builtins__': __builtins__,
            'pl': pl  # Include necessary libraries in the execution environment
        }
        
    def get_embedding(self, document: Dict[str, Any]):
        text = f"{document.get('name', '')} {document.get('short_description', '')} {document.get('long_description', '')}"
        embedding = OpenAIAPI.generate_embedding(text)
        return embedding
    
    def update_conditions_embeddings(self):
        conditions = self.find_all()
        for condition in conditions:
            embedding = self.get_embedding(condition.model_dump())
            self.dal.update_condition_embeddings(condition.id,embedding)

    def generate_condition(self, prompt: str):
        # message =  self.assistant.chat(prompt)
        message_dict = message.model_dump()
        compiled_calc = self.get_compiled_calc_pl(message_dict['calc_pl'], message_dict['symbol'], message_dict['required_calculations'])
        validate_generated_script(compiled_calc['calc_pl'],message_dict['params'])
        doc = self.insert_one(message_dict)
        return doc
        

    def insert_one(self, document: Dict[str, Any], session: ClientSession | None = None):
        return super().insert_one(document, session)
    
    def add(self, cond_data: dict):
        """
        Adds a new condition to the database and compiles it for execution.
        """
        try:
            # Validate the condition data
            new_condition = ConditionsModel(**cond_data)
            # Save the condition to MongoDB
            self.dal.insert_one(new_condition.model_dump(by_alias=True))
            return {"status": "success", "message": "Condition added and compiled."}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_compiled_calc_pl(self, calc_pl:str, symbol:str,required_calculations:List[str]) -> CompiledCalc:
        """
        Compiles the class definition and adds it to the namespace for execution.
        """
        if not calc_pl:
            raise ValueError("No calc_pl found in the calculation data.")

        if symbol in self.execution_namespace:
            return  self.execution_namespace[symbol] # Already compiled, no need to recompile

        # Compile required calculations first
        calc_bl = CalculationsBl()
        all_compiled_calcs = {}
        for required_symbol in required_calculations:
            calculation = calc_bl.dal.get_calculation_by_symbol(required_symbol.lower())
            compiled_calc = calc_bl.get_calculation_as_compiled_class(calculation)
            calc_dict = {required_symbol: compiled_calc}
            all_compiled_calcs = {**all_compiled_calcs, **calc_dict}

        self.compiled_calculations = {**self.compiled_calculations, **all_compiled_calcs}
        
        # Create temporary namespace for compilation
        temp_namespace = {}
        
        # Compile and execute the condition code
        code_obj = compile(calc_pl, f"<condition {symbol}>", 'exec')
        exec(code_obj, {**self.execution_namespace, **self.compiled_calculations}, temp_namespace)

        self.compiled_conditions[symbol] = temp_namespace
        self.execution_namespace[symbol] = temp_namespace

        return self.execution_namespace[symbol]

    def execute_condition(self, class_name: str, params: dict, dfs: pl.DataFrame):
        """
        Executes the specified condition on the provided DataFrame.
        """
        try:

            # Retrieve and instantiate the condition class
            cond_class = self.compiled_conditions[class_name]()
            # Execute the 'calc' method of the condition class
            return cond_class.calc(dfs, params)
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def update(self, symbol: str, update_data: dict):
        """
        Updates an existing condition by its symbol.
        """
        try:
            self.dal.update(symbol, update_data)
            return {"status": "success", "message": "Condition updated."}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def delete(self, symbol: str):
        """
        Deletes a condition from the database.
        """
        try:
            self.dal.delete(symbol)
            return {"status": "success", "message": "Condition deleted."}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def generate_documentation(self):
        """
        Generates and saves documentation for all conditions in the system.
        """
        try:
            self.documenter.generate_documentation()
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

    def load_and_insert_conditions(self):
        """
        Loads all JSON files from the 'src/features/conditions/jsons' folder
        and inserts them into the database.
        """
        json_folder = "src/features/big_data/conditions/dicts"
        
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
            
            # Process Python files with dictionaries            elif file.endswith('.py'):
            else:
                try:
                    data = self.load_python_file(file_path)
                    logging.info(f"Loaded Python file: {file}")
                    
                    # Insert data into the database
                    self.dal.insert_one(self.snake_to_camel(data))
                    logging.info(f"Inserted data from {file} into the database.")
                
                except Exception as e:
                    logging.error(f"Error loading or inserting data from {file}: {e}")

                    
    
    def get_condition_by_symbol(self, symbol: str):
        return self.dal.get_by_symbol(symbol)

    def find_similar_conditions(self, embedding, top_k=5):
        return self.dal.find_similar_conditions(embedding, top_k)
