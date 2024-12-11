import os
from typing import Dict

class CalculationFileGenerator:
    def __init__(self, calc_data: Dict):
        self.calc_data = calc_data
        self.output_dir = "calculations/calcs"
        os.makedirs(self.output_dir, exist_ok=True)

    def create_calc_file(self):
        symbol = self.calc_data["symbol"]
        calc_pl_code = self.calc_data["calc_pl"]
        file_path = os.path.join(self.output_dir, f"{symbol}.py")

        with open(file_path, "w") as file:
            file.write(f"# {self.calc_data['name']}\n\n")
            file.write(calc_pl_code)
        
        return file_path

    def generate_main_dict_file(self, all_calc_data: Dict[str, Dict]):
        main_dict_path = os.path.join(self.output_dir, "all_calculations.py")
        
        with open(main_dict_path, "w") as main_file:
            main_file.write("all_calculations = {\n")

            for symbol, data in all_calc_data.items():
                main_file.write(f"    '{symbol}': {{\n")
                main_file.write(f"        'name': '{data['name']}',\n")
                main_file.write(f"        'symbol': '{data['symbol']}',\n")
                main_file.write(f"        'calc_pl': {data['calc_pl']},\n")
                main_file.write("    },\n")

            main_file.write("}\n")
        
        return main_dict_path

    def execute(self, all_calc_data: Dict[str, Dict]):
        # Create individual calculation file for the current calc_data
        self.create_calc_file()
        
        # Generate a main dictionary file for all calculations
        self.generate_main_dict_file(all_calc_data)
