import yaml
import os

from common.services.models.calculations_model import CalculationsModel



class CalculationsDocumenter:
    def __init__(self, output_dir='./docs', max_file_size=100):
        self.output_dir = output_dir
        self.max_file_size = max_file_size * 1024 * 1024  # Convert MB to bytes
        os.makedirs(self.output_dir, exist_ok=True)

    def document_calculation(self, calc_data:CalculationsModel):
        """Generates a minimal documentation for a single calculation."""
        return {
            "symbol": calc_data.symbol,
            "description": calc_data.short_description,
            "usage_example": calc_data.programmer_usage_example,
            "returns_structure": calc_data.returns_structure_of_calc_pl.model_dump()
        }

    def save_to_file(self, data, file_index):
        """Saves the data as a text file ensuring it's minimal in size."""
        file_path = os.path.join(self.output_dir, f'calculations_doc_{file_index}.txt')

        # Write data as plain text
        with open(file_path, 'w', encoding='utf-8') as f:
            for item in data:
                f.write(f"Symbol: {item['symbol']}\n")
                f.write(f"Description: {item['description']}\n")
                f.write(f"Usage Example: {item['usage_example']}\n")
                f.write(f"Returns Structure: {item['returns_structure']}\n")
                f.write("\n---\n\n")  # Separator between entries

    def generate_documentation(self,calculations:list[CalculationsModel]):
        """Generates minimal documentation files ensuring each is under 100MB (uncompressed)."""
        total_size = 0
        doc_list = []
        file_index = 0

        for calc_data in calculations:
            doc_content = self.document_calculation(calc_data)
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

