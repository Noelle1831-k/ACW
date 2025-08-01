import os
import json
import fire


class PythonFileConverter:
    def __init__(self, input_folder, language='python', EXT='py'):
        self.language = language
        self.EXT = EXT
        self.input_folder = input_folder
    
    def convert_py_folder_to_jsonl(self, output_file):
        with open(output_file, 'w', encoding='utf-8') as outfile:
            for filename in os.listdir(self.input_folder):
                if filename.endswith(f'.{self.EXT}'):
                    file_path = os.path.join(self.input_folder, filename)
                    with open(file_path, 'r', encoding='utf-8') as py_file:
                        code_content = py_file.read()
                    json_item = {
                        "task_id": os.path.splitext(filename)[0].replace('_', '/'),
                        "completion": code_content,
                        "language": self.language
                    }
                    outfile.write(json.dumps(json_item, ensure_ascii=False) + '\n')
        
        print(f"Conversion completed! JSONL file saved as {output_file}")


if __name__ == '__main__':
    fire.Fire(PythonFileConverter)
