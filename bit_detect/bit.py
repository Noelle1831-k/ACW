import os
from base import folder_list
from base import formatting
from one_rule_format import single_process_file

T_cor = 0
N_cor = 0
T_ori = 0
N_ori = 0

def bit_split(bits, path, file):
	bit_list = [int(bit) for bit in bits]
	parts = file.split('-')
	numbers = parts[1:-1] + [parts[-1].split('.')[0]]
	numbers_int = [int(num) for num in numbers]
	for loc, bit in enumerate(bit_list):
		if bit == 1:
			single_process_file(numbers_int[loc], os.path.join(path, file))


def bit_detect(path, file):
	bit_list = [1, 1, 1, 1]
	detect_list = []
	file_path = os.path.join(path, file)
	original_content, _ = formatting.read_file_with_auto_encoding(file_path)
	parts = file.split('-')
	numbers = parts[1:-1] + [parts[-1].split('.')[0]]
	numbers_int = [int(num) for num in numbers]

	for loc in range(4):
		if bit_list[loc] == 1:
			single_process_file(numbers_int[loc], file_path)
			new_content, _ = formatting.read_file_with_auto_encoding(file_path)
			detect_list.append(1 if original_content == new_content else 0)
			# 恢复原始内容
			with open(file_path, 'w', encoding='utf-8') as f:
				f.writelines(original_content)

	return detect_list


def bit_correct(detect_list):
	wrong_patterns = {
		(0, 0, 0, 0): [[0, 0, 0, 1], [0, 0, 1, 0], [0, 1, 0, 0], [1, 0, 0, 0]],
		(0, 1, 0, 1): [[1, 1, 0, 1], [0, 1, 1, 1]],
		(1, 0, 1, 0): [[1, 1, 1, 0], [1, 0, 1, 1]]
	}

	for correct, wrong in wrong_patterns.items():
		if detect_list in wrong:
			return list(correct), True
	return detect_list, False


def bit_compare(detect_list, bit_list):
	if detect_list == bit_list:
		return True, False
	corrected_list, flag = bit_correct(detect_list)
	return flag and corrected_list == bit_list, True


def process_folders():
	global T_ori, N_ori, T_cor, N_cor
	for folder_path in folder_list.folder_paths:
		python_files = [f for f in os.listdir(folder_path) if f.endswith('.py')]
		for file in python_files:
			bit_split('0101', folder_path, file)
			detect_list = bit_detect(folder_path, file)
			print(detect_list)
			compare_flag, correct_flag = bit_compare(detect_list, [0, 1, 0, 1])
			if correct_flag:
				if compare_flag:
					T_cor += 1
					N_ori += 1
				else:
					N_ori += 1
			else:
				T_ori += 1
		print(f'{folder_path} detect acc without correcting:{T_ori/(T_ori+N_ori)},with correcting:{(T_ori+T_cor)/(T_ori+N_ori)}')


if __name__ == "__main__":
	process_folders()
