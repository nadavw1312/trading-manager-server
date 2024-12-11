import yaml
import os
from pymongo import MongoClient

class ConditionsDocumenter:
    def __init__(self, db_name='conditions_db', collection_name='conditions', output_dir='./docs', max_file_size=100):
        self.client = MongoClient()  # Adjust with your MongoDB connection details if needed
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        self.output_dir = output_dir
        self.max_file_size = max_file_size * 1024 * 1024  # Convert MB to bytes
        os.makedirs(self.output_dir, exist_ok=True)
        
    def fetch_all_conditions(self):
        """Fetches all conditions from the database."""
        return self.collection.find({})

    def document_condition(self, cond_data):
        """Generates minimal documentation for a single condition."""
        return {
            "symbol": cond_data.get('symbol', ''),
            "description": cond_data.get('description', ''),
            "usage_example": cond_data.get('usage_example', ''),
            "params": cond_data.get('params', '')
        }

    def save_to_file(self, data, file_index):
        """Saves the data as a YAML file ensuring it's minimal in size."""
        file_path = os.path.join(self.output_dir, f'conditions_doc_{file_index}.yaml')

        # Write YAML directly
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False)  # Write YAML in a readable format

    def generate_documentation(self):
        """Generates minimal documentation files ensuring each is under 100MB (uncompressed)."""
        conditions = self.fetch_all_conditions()
        total_size = 0
        doc_list = []
        file_index = 0

        for cond_data in conditions:
            doc_content = self.document_condition(cond_data)
            doc_list.append(doc_content)

            # Estimate the size of the batch in bytes after converting to YAML
            current_size = len(yaml.dump(doc_list, default_flow_style=False).encode('utf-8'))

            if total_size + current_size > self.max_file_size:
                self.save_to_file(doc_list, file_index)
                file_index += 1
                doc_list = []
                total_size = 0  # Reset after saving

            total_size += current_size

        if doc_list:
            self.save_to_file(doc_list, file_index)  # Save any remaining docs

