import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

from folder_list import folder_paths


def run_autopep8(file_path):
	commands = [
		["autopep8", "--in-place", "--select=E225,E226,E227,E228,E241,E242,E251,E252,E231", "--verbose", file_path],
		["autopep8", "--in-place", "--select=E27", "--verbose", file_path],
		["autopep8", "--in-place", "--select=E123", "--verbose", file_path],
		["autopep8", "--in-place", "--select=W292", "--verbose", file_path],
		["autopep8", "--in-place", "--select=E301,E302,E305,E306", "--verbose", file_path],
	]

	for command in commands:
		result = subprocess.run(command, capture_output=True, text=True)
		if result.returncode != 0:
			return f"Error running autopep8 on {file_path}: {result.stderr}"
	return f"autopep8 ran successfully on {file_path}"


def process_files_in_folder(folder_path, c):
	new_folder_path = os.path.join(folder_path, folder_path[2:] + c)
	if not os.path.exists(new_folder_path):
		return f"Directory does not exist: {new_folder_path}"

	python_files = [f for f in os.listdir(new_folder_path) if f.endswith('.py')]
	results = []
	with ThreadPoolExecutor() as executor:
		futures = [executor.submit(run_autopep8, os.path.join(new_folder_path, file)) for file in python_files]
		for future in as_completed(futures):
			results.append(future.result())
	return results


if __name__ == "__main__":

	C = [
		"_1",
		"_2",
		"_3",
		"_4",
		"_5",
		"_6",
		"_over6"
	]

	overall_results = []
	for folder_path in folder_paths:
		for c in C:
			folder_results = process_files_in_folder(folder_path, c)
			overall_results.extend(folder_results)

	for result in overall_results:
		print(result)
