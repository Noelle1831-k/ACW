import os
import subprocess

import folder_list
import refact_list
from rename_sourcery import rename

# 定义要执行的命令和参数
C = [
		"_1",
		"_2",
		"_3",
		"_4",
		"_5",
		"_6",
		"_over6"
	]
i = 1
for refactoring in refact_list.refactoring_list:
	for folder_path in folder_list.folder_paths:
			# for c in C:
			# 	path = os.path.join(folder_path, folder_path[2:] + c)
				# command = [
				# 	'sourcery',
				# 	'review',
				# 	'--fix',
				# 	'--config',
				# 	'.sourcery.yaml',
				# 	'--verbose',
				# 	folder_path
				# ]
				# # # 定义输出文件路径
				output_file_path = folder_path + f'/{i}.txt'
				#
				# # # 构建命令字符串
				# command_str = ' '.join(command) + f' > {output_file_path}'
				#
				# # # 使用 subprocess.run 执行命令
				# result = subprocess.run(command_str, shell=True, text=True)

				# 检查命令的返回码
				# if result.returncode == 0:
				# 	print(f"Command executed successfully.")
				rename(output_file_path, i)
				# else:
				# 	print("Command failed with return code:", result.returncode)

	i += 1