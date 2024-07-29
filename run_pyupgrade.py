import os
import subprocess

import refact_list
from folder_list import folder_paths
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
# for refactoring in refact_list.refactoring_list:
for folder_path in folder_paths:
	for c in C:
		path = os.path.join(folder_path, folder_path[2:] + c)
		files_to_process = [os.path.join(path, file) for file in os.listdir(path) if file.endswith('.py')]
		for file in files_to_process:
			command = [
				'pyupgrade',
				file
			]

			result = subprocess.run(command, text=True)

			# 检查命令的返回码
			if result.returncode == 0:
				print(f"Command executed successfully.")
			else:
				print("Command failed with return code:", result.returncode)
