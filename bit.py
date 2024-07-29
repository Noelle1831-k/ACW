import os

import folder_list
import formatting
from one_rule_format import single_process_file

T = 0
N = 0


def bit_spilt(bits, path, file):
	bit_list = [int(bit) for bit in bits]
	for loc in range(0, 4):
		if bit_list[loc] == 1:
			parts = file.split('-')
			numbers = parts[1:-1] + [parts[-1].split('.')[0]]
			numbers_int = [int(num) for num in numbers]
			single_process_file(numbers_int[loc], os.path.join(path, file))


def bit_detect(path, file):
	bit_list = [1, 1, 1, 1]
	detect_list = [0, 0, 0, 0]
	file_path = os.path.join(path, file)
	for loc in range(0, 4):
		if bit_list[loc] == 1:
			original_content = formatting.read_file_with_auto_encoding(file_path)
			parts = file.split('-')
			numbers = parts[1:-1] + [parts[-1].split('.')[0]]
			numbers_int = [int(num) for num in numbers]
			single_process_file(numbers_int[loc],file_path)
			new_content = formatting.read_file_with_auto_encoding(file_path)
			if not original_content == new_content:
				detect_list[loc] = 0
			else:
				detect_list[loc] = 1
	return detect_list


def bit_compare(detect_list, bit_list):
	if detect_list == bit_list:
		return True
	else:
		detect_list, flag = bit_correct(detect_list)
		if flag:
			if detect_list == bit_list:
				return True
			else:
				return False


def bit_correct(detect_list):
	wrong_0000 = [[0, 0, 0, 1], [0, 0, 1, 0], [0, 1, 0, 0], [1, 0, 0, 0]]
	wrong_0101 = [[1, 1, 0, 1], [0, 1, 1, 1]]
	wrong_1010 = [[1, 1, 1, 0], [1, 0, 1, 1]]
	if detect_list in wrong_0000:
		detect_list = [0, 0, 0, 0]
		return True, detect_list
	elif detect_list in wrong_0101:
		detect_list = [0, 1, 0, 1]
		return True, detect_list
	elif detect_list in wrong_1010:
		detect_list = [1, 0, 1, 0]
		return True, detect_list
	else:
		return False


for folder_path in folder_list.folder_paths:
	python_files = [f for f in os.listdir(folder_path) if f.endswith('.py')]
	for file in python_files:
		bit_spilt('0000', file)
		detect_list = bit_detect(folder_path, file)
		if bit_compare(detect_list, [0,0,0,0]):
			T += 1
		else:
			N += 1

