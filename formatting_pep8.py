import ast
import os

import autopep8


def fix_missing_space(folder_paths):
	for folder_path in folder_paths:
		python_files = [f for f in os.listdir(folder_path) if f.endswith('.py')]
		for file in python_files:
			file_path = os.path.join(folder_path, file)
			try:
				with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
					original_code = f.read()
					lines = original_code.split('\n')
				tree = ast.parse(original_code)
				select_rules = ['E225', 'E226', 'E227', 'E228', 'E241', 'E242', 'E251', 'E252', 'E231']
				formatted_code = autopep8.fix_code(original_code, options={'select': select_rules})
				if formatted_code != original_code:
					new_file_path = file_path[:-3] + '-40.py'
					# print(new_file_path)
					os.rename(file_path, new_file_path)
			except Exception as e:
				print(f"Error processing file {file_path}: {e}")


def fix_over_space(folder_paths):
	for folder_path in folder_paths:

		python_files = [f for f in os.listdir(folder_path) if f.endswith('.py')]
		for file in python_files:
			file_path = os.path.join(folder_path, file)
			try:
				with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
					original_code = f.read()
					lines = original_code.split('\n')
				tree = ast.parse(original_code)
				select_rules = ['E27']
				formatted_code = autopep8.fix_code(original_code, options={'select': select_rules})
				if formatted_code != original_code:
					new_file_path = file_path[:-3] + '-41.py'
					# print(new_file_path)
					os.rename(file_path, new_file_path)
			except Exception as e:
				print(f"Error processing file {file_path}: {e}")


def align_bracket(folder_paths):
	for folder_path in folder_paths:

		python_files = [f for f in os.listdir(folder_path) if f.endswith('.py')]
		for file in python_files:
			file_path = os.path.join(folder_path, file)
			try:
				with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
					original_code = f.read()
					lines = original_code.split('\n')
				tree = ast.parse(original_code)
				select_rules = ['E123']
				formatted_code = autopep8.fix_code(original_code, options={'select': select_rules})
				if formatted_code != original_code:
					new_file_path = file_path[:-3] + '-42.py'
					# print(new_file_path)
					os.rename(file_path, new_file_path)
			except Exception as e:
				print(f"Error processing file {file_path}: {e}")


def new_line_after_end(folder_paths):
	for folder_path in folder_paths:

		python_files = [f for f in os.listdir(folder_path) if f.endswith('.py')]
		for file in python_files:
			file_path = os.path.join(folder_path, file)
			try:
				with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
					original_code = f.read()
					lines = original_code.split('\n')
				tree = ast.parse(original_code)

				# 44
				select_rules = ['W292']
				formatted_code = autopep8.fix_code(original_code, options={'select': select_rules})
				if formatted_code != original_code:
					new_file_path = file_path[:-3] + '-43.py'
					# print(new_file_path)
					os.rename(file_path, new_file_path)
			except Exception as e:
				print(f"Error processing file {file_path}: {e}")


def add_blank_line(folder_paths):
	for folder_path in folder_paths:

		python_files = [f for f in os.listdir(folder_path) if f.endswith('.py')]

		for file in python_files:
			file_path = os.path.join(folder_path, file)
			try:
				with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
					original_code = f.read()
					lines = original_code.split('\n')
				tree = ast.parse(original_code)
				select_rules = ['E301', 'E302', 'E305', 'E306']
				formatted_code = autopep8.fix_code(original_code, options={'select': select_rules})
				if formatted_code != original_code:
					new_file_path = file_path[:-3] + '-44.py'
					# print(new_file_path)
					os.rename(file_path, new_file_path)

			except Exception as e:
				print(f"Error processing file {file_path}: {e}")