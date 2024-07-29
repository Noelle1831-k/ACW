import os

if __name__ == "__main__":
	folder_paths_G = [
		"G/APPS_3.5_G",
		"G/APPS_4_G",
		"G/MBPP_3.5_G",
		"G/MBPP_4_G",
		"G/MBPP_Starcoder_G"
	]
	folder_paths_H = [
		"H/APPS_3.5_H",
		"H/APPS_4_H",
		"H/MBPP_3.5_H",
		"H/MBPP_4_H",
		"H/MBPP_Starcoder_H"

	]
	num_G = [[0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0]]
	num_H = [[0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0]]

	num_of_set = 0
	for folder_path in folder_paths_G:

		python_files = [f for f in os.listdir(folder_path) if f.endswith('.py')]
		for file in python_files:
			file_path = os.path.join(folder_path, file)
			index = file.count('-')
			if 0 <= index <= 6:
				new_name = os.path.join(folder_path, folder_path[2:] + '_' + str(index), file)
				# print(new_name)
				os.makedirs(os.path.dirname(new_name), exist_ok=True)
				os.rename(file_path, new_name)
				num_G[num_of_set][index] += 1
			elif index > 6:
				new_name = os.path.join(folder_path, folder_path[2:] + '_over6', file)
				# print(new_name)
				os.makedirs(os.path.dirname(new_name), exist_ok=True)
				os.rename(file_path, new_name)
				num_G[num_of_set][7] += 1
		num_of_set += 1
	num_of_set = 0
	# for folder_path in folder_paths_H:
	#
	# 	python_files = [f for f in os.listdir(folder_path) if f.endswith('.py')]
	# 	for file in python_files:
	# 		file_path = os.path.join(folder_path, file)
	# 		index = file.count('-')
	# 		if 0 <= index <= 6:
	# 			new_name = os.path.join(folder_path, folder_path[2:] + '_' + str(index), file)
	# 			os.makedirs(os.path.dirname(new_name), exist_ok=True)
	# 			# print(new_name)
	# 			os.rename(file_path, new_name)
	# 			num_H[num_of_set][index] += 1
	# 		elif index > 6:
	# 			new_name = os.path.join(folder_path, folder_path[2:] + '_over6', file)
	# 			os.makedirs(os.path.dirname(new_name), exist_ok=True)
	# 			# print(new_name)
	# 			os.rename(file_path, new_name)
	# 			num_H[num_of_set][7] += 1
	# 	num_of_set += 1
	print(num_G)
	print(num_H)
	num_final = [[0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0]]
	for x in range(5):
		for y in range(8):
			num_final[x][y] = min(num_G[x][y], num_H[x][y])
	print(num_final)
