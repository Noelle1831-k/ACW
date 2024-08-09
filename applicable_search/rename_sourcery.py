import re
import os


def rename(input_file_path, number):
	with open(input_file_path, 'r', encoding='utf-8') as file:
		lines = file.readlines()
	pattern = r'Reviewed ([^/\\]+[/\\][^/\\]+[/\\])([^/\\]+\.py)'
	for line in lines:
		match = re.search(pattern, line)
		if match:
			path = match.group(1)
			filename = match.group(2)
			old_file_path = os.path.join(path, filename)

			replacement = r'-{}\1'.format(number)
			new_filename = re.sub(r'(\.py)$', replacement, filename)
			new_file_path = os.path.join(path, new_filename)

			if os.path.exists(old_file_path):
				os.rename(old_file_path, new_file_path)
				print(f"Renamed: {old_file_path} -> {new_file_path}")
			else:
				print(f"File does not exist: {old_file_path}")