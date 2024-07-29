import os

import folder_list
from folder_list import folder_paths
from one_rule_format import single_process_file

C = [
	"_1",
	"_2",
	"_3",
	"_4",
	"_5",
	"_6",
	"_over6",
]
for folder_path in folder_list.folder_paths:
	for c in C:
		path = os.path.join(folder_path, folder_path[2:] + c)
		python_files = [f for f in os.listdir(path) if f.endswith('.py')]
		for file in python_files:
			parts = file.split('-')
			numbers = parts[1:-1] + [parts[-1].split('.')[0]]
			numbers_int = [int(num) for num in numbers]
			print(os.path.join(path,file))
			single_process_file(numbers_int[0],os.path.join(path,file))