import os

import openpyxl

if __name__ == "__main__":
	folder_paths = [
		"G/MBPP_3.5_G",
		"G/MBPP_4_G",
		"G/APPS_3.5_G",
		"G/APPS_4_G",
		"G/MBPP_Starcoder_G"

	]
	C = [
		"_1",
		"_2",
		"_3",
		"_4",
		"_5",
		"_6",
		"_over6",
	]
	results = [0 for _ in range(35)]
	count_set = 0
	for folder_path in folder_paths:
		for c in C:
			count_set += 1
			new_folder_path = os.path.join(folder_path, folder_path[2:] + c)
			python_files = [f for f in os.listdir(new_folder_path) if f.endswith('.py')]
			count_line = 0
			count_file = 0
			for file in python_files:
				file_path = os.path.join(new_folder_path, file)
				try:
					with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
						original_code = f.readlines()
						count_file += 1
						lines = len(original_code)
						count_line += lines
				except Exception as e:
					print(f"Error processing file {file_path}: {e}")
			if count_file > 0:
				results[count_set - 1] = count_line / count_file
			else:
				results[count_set - 1] = 0
	workbook = openpyxl.Workbook()
	sheet = workbook.active
	sheet.title = 'Count'

	for row_num, result in enumerate(results):
		sheet.cell(row=row_num + 1, column=1, value=result)

	workbook.save('count.xlsx')