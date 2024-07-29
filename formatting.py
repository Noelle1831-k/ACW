import re
import tempfile

import chardet


def detect_encoding(file_path):    # 检测编码格式
	with open(file_path, 'rb') as file:
		raw_data = file.read()
	result = chardet.detect(raw_data)
	return result['encoding']


def read_file_with_auto_encoding(file_path):    # 以自动检测的编码格式或预设编码格式进行文件读取
	encodings_to_try = ['utf-8', 'gbk']
	detected_encoding = detect_encoding(file_path)
	if detected_encoding:
		encodings_to_try.insert(0, detected_encoding)

	for encoding in encodings_to_try:
		try:
			with open(file_path, 'r', encoding=encoding) as file:
				return file.readlines(), encoding
		except UnicodeDecodeError:
			continue

	raise ValueError(f"Unable to determine the correct encoding for {file_path}")


def add_space_in_comments(line):    # 注释前加入空格，防止E262错误
	if line.strip().startswith('#'):
		if not line.startswith('# '):
			line = '# ' + line[1:].lstrip()
	return line


def merge_code_and_comments(input_file, output_file):   # 注释和代码合并
	lines, detected_encoding = read_file_with_auto_encoding(input_file)
	merged_lines = []
	i = 0
	while i < len(lines):
		current_line = lines[i].rstrip('\n\r')

		if current_line.strip() and not current_line.strip().startswith('#'):
			# 当前行不能是注释
			if i + 1 < len(lines) and lines[i + 1].strip().startswith('#'):
				# 寻找注释
				if (i + 2 < len(lines) and not lines[i + 2].strip().startswith('#')) or i + 2 == len(lines):
					# 判断防止修改连续注释行存在
					comment = lines[i + 1].strip()
					comment = add_space_in_comments(comment)
					merged_line = f"{current_line}  {comment}"
					merged_lines.append(merged_line)
					i += 2  # 合并一行，向下移动两行
				else:
					merged_lines.append(current_line)
					i += 1
			else:
				merged_lines.append(current_line)
				i += 1
		else:
			merged_lines.append(current_line)
			i += 1
	if lines and lines[-1].endswith('\n'):
		merged_lines.append('')
	# with open(output_file, 'w', encoding=detected_encoding) as file:
	# 	file.write('\n'.join(merged_lines))
	# 	return output_file
	# 如果需要对文件进行直接修改则使用上述代码，抛弃下面的代码
	with tempfile.NamedTemporaryFile(delete=False, mode='w', encoding=detected_encoding) as temp_file:
		temp_file.write('\n'.join(merged_lines))
		temp_file_path = temp_file.name
	return temp_file_path


def convert_spaces_to_tabs(file_path, spaces_per_tab=4):
	lines, encoding = read_file_with_auto_encoding(file_path)
	new_lines = []
	for line in lines:
		leading_spaces = len(line) - len(line.lstrip(' '))
		tabs = leading_spaces // spaces_per_tab
		new_line = '\t' * tabs + line.lstrip(' ')
		new_lines.append(new_line)
	# with open(file_path, 'w', encoding=encoding) as file:
	# 	file.writelines(new_lines)
	# 如果需要对文件进行直接修改则使用上述代码，抛弃下面的代码
	with tempfile.NamedTemporaryFile(delete=False, mode='w', encoding=encoding) as temp_file:
		temp_file.writelines(new_lines)
		temp_file_path = temp_file.name
	return temp_file_path
