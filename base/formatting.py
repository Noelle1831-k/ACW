import tempfile

import chardet


def detect_encoding(file_path):
	with open(file_path, 'rb') as file:
		raw_data = file.read()
	result = chardet.detect(raw_data)
	return result['encoding']


def read_file_with_auto_encoding(file_path):
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


def add_space_in_comments(line):
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
			if i + 1 < len(lines) and lines[i + 1].strip().startswith('#'):
				if (i + 2 < len(lines) and not lines[i + 2].strip().startswith('#')) or i + 2 == len(lines):
					comment = lines[i + 1].strip()
					comment = add_space_in_comments(comment)
					merged_line = f"{current_line}  {comment}"
					merged_lines.append(merged_line)
					i += 2
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

	with tempfile.NamedTemporaryFile(delete=False, mode='w', encoding=encoding) as temp_file:
		temp_file.writelines(new_lines)
		temp_file_path = temp_file.name
	return temp_file_path
