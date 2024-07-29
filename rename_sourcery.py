import re
import os


def rename(input_file_path, number):
	with open(input_file_path, 'r', encoding='utf-8') as file:
		lines = file.readlines()
	# 定义正则表达式模式来识别路径
	pattern = r'Reviewed ([^/\\]+[/\\][^/\\]+[/\\])([^/\\]+\.py)'
	for line in lines:
		# 使用正则表达式查找匹配
		match = re.search(pattern, line)
		if match:
			# 获取匹配的路径和文件名
			path = match.group(1)
			filename = match.group(2)
			old_file_path = os.path.join(path, filename)

			# 修改文件名
			replacement = r'-{}\1'.format(number)
			new_filename = re.sub(r'(\.py)$', replacement, filename)
			new_file_path = os.path.join(path, new_filename)

			# 重命名文件
			if os.path.exists(old_file_path):
				os.rename(old_file_path, new_file_path)
				print(f"Renamed: {old_file_path} -> {new_file_path}")
			else:
				print(f"File does not exist: {old_file_path}")