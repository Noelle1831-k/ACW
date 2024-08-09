import os

import concurrent.futures

from base import formatting_pep8
from base import folder_list

C = [
	"_1",
	"_2",
	"_3",
	"_4",
	"_5",
	"_6",
	"_over6",
]


# def process_file_merge_comment(file_path):
#
# 	original_content = formatting.read_file_with_auto_encoding(file_path)
# 	temp_path = formatting.merge_code_and_comments(file_path, file_path)
# 	new_content = formatting.read_file_with_auto_encoding(file_path)
# 	os.remove(temp_path)
# 	return file_path, original_content != new_content


def process_file_tab(file_path):
	original_content = formatting_pep8.read_file_with_auto_encoding(file_path)
	temp_path = formatting_pep8.convert_spaces_to_tabs(file_path)
	new_content = formatting_pep8.read_file_with_auto_encoding(temp_path)
	os.remove(temp_path)
	return file_path, original_content != new_content


def batch_process_files_tab(directory='.', max_workers=16):
	modified_files_count = 0
	unmodified_files_count = 0
	files_to_process = [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith('.py')]
	with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
		future_to_file = {executor.submit(process_file_tab, file): file for file in files_to_process}
		for future in concurrent.futures.as_completed(future_to_file):
			file_path, modified = future.result()
			if modified:
				modified_files_count += 1
				new_file_path = file_path[:-3] + '-45.py'
				os.rename(file_path, new_file_path)
			else:
				unmodified_files_count += 1
			print(f"Processed file: {file_path} - {'Modified' if modified else 'Unmodified'}")
			print(f"modified_files_count_50 ={modified_files_count}")


"""
deleted rule
"""
# def batch_process_files_merge(directory='.', max_workers=16):
#
# 	modified_files_count = 0
# 	unmodified_files_count = 0
# 	files_to_process = [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith('.py')]
# 	with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
# 		future_to_file = {executor.submit(process_file_merge_comment, file): file for file in files_to_process}
# 		for future in concurrent.futures.as_completed(future_to_file):
# 			file_path, modified = future.result()
# 			if modified:
# 				modified_files_count += 1
# 				new_file_path = file_path[:-3] + '-46.py'
# 				os.rename(file_path, new_file_path)
# 			else:
# 				unmodified_files_count += 1
# 			print(f"Processed file: {file_path} - {'Modified' if modified else 'Unmodified'}")
# 			print(f"modified_files_count_46 ={modified_files_count}")


formatting_pep8.fix_missing_space(folder_list.folder_paths)
formatting_pep8.fix_over_space(folder_list.folder_paths)
formatting_pep8.align_bracket(folder_list.folder_paths)
formatting_pep8.new_line_after_end(folder_list.folder_paths)
formatting_pep8.add_blank_line(folder_list.folder_paths)
for folder_path in folder_list.folder_paths:
	# for c in C:
	# 	path = os.path.join(folder_path, folder_path[2:] + c)
		batch_process_files_tab(folder_path)
