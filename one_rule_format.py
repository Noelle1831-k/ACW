import ast
import hashlib
import subprocess

import astor

import refact_list
from formatting import read_file_with_auto_encoding
from run_test_1 import (transform_operations_add, transform_operations_mult,transform_comparison_LG
	,transform_comparison_LGE)


def single_process_file(index, file_path):
	if 1 <= index <= 35:
		sourcery_process(index, file_path)
	elif 36 <= index <= 39:
		reorder_process(index, file_path)
	elif 40 <= index <= 44:
		reformatting_process(index, file_path)
	elif index == 45:
		tab_convert_process(index, file_path)


def sourcery_process(index, file_path):
	refactor_rule = refact_list.refactoring_list[index - 1]
	command = [
		'sourcery',
		'review',
		'--fix',
		'--enable',
		refactor_rule,
		'--verbose',
		file_path
	]
	result = subprocess.run(command, text=True)
	# 检查命令的返回码
	if result.returncode == 0:
		print(f"rule {index} exec succeeded on {file_path}")
	else:
		print("Command failed with return code:", result.returncode)


def reorder_process(index, file_path):
	if index == 36:
		try:
			with open(file_path, 'r') as file:
				content = file.read()
				lines = content.split('\n')
			tree = ast.parse(content)
			for node in ast.walk(tree):
				transform_operations_add(node, lines, file_path, tree)
		except Exception as e:
			print(f"Error processing file {file_path}: {e}")
		else:
			print(f"rule {index} exec succeeded on {file_path}")
	elif index == 37:
		try:
			with open(file_path, 'r') as file:
				content = file.read()
				lines = content.split('\n')
			tree = ast.parse(content)
			for node in ast.walk(tree):
				transform_operations_mult(node, lines, file_path, tree)
		except Exception as e:
			print(f"Error processing file {file_path}: {e}")
		else:
			print(f"rule {index} exec succeeded on {file_path}")
	elif index == 38:
		try:
			with open(file_path, 'r') as file:
				content = file.read()
				lines = content.split('\n')
			tree = ast.parse(content)
			for node in ast.walk(tree):
				transform_comparison_LG(node, lines, file_path, tree)
		except Exception as e:
			print(f"Error processing file {file_path}: {e}")
		else:
			print(f"rule {index} exec succeeded on {file_path}")
	elif index == 39:
		try:
			with open(file_path, 'r') as file:
				content = file.read()
				lines = content.split('\n')
			tree = ast.parse(content)
			for node in ast.walk(tree):
				transform_comparison_LGE(node, lines, file_path, tree)
		except Exception as e:
			print(f"Error processing file {file_path}: {e}")
		else:
			print(f"rule {index} exec succeeded on {file_path}")


def reformatting_process(index, file_path):
	commands = [
		["autopep8", "--in-place", "--select=E225,E226,E227,E228,E241,E242,E251,E252,E231", "--verbose", file_path],
		["autopep8", "--in-place", "--select=E27", "--verbose", file_path],
		["autopep8", "--in-place", "--select=E123", "--verbose", file_path],
		["autopep8", "--in-place", "--select=W292", "--verbose", file_path],
		["autopep8", "--in-place", "--select=E301,E302,E305,E306", "--verbose", file_path],
	]
	command = commands[index - 40]
	result = subprocess.run(command, capture_output=True, text=True)
	if result.returncode != 0:
		print(f"rule {index} exec failed on {file_path}")
	else:
		print(f"rule {index} exec succeeded on {file_path}")


def tab_convert_process(index, file_path, spaces_per_tab=4):
	lines, encoding = read_file_with_auto_encoding(file_path)
	new_lines = []
	for line in lines:
		leading_spaces = len(line) - len(line.lstrip(' '))
		tabs = leading_spaces // spaces_per_tab
		new_line = '\t' * tabs + line.lstrip(' ')
		new_lines.append(new_line)
	try:
		with open(file_path, 'w', encoding=encoding) as file:
			file.writelines(new_lines)
	except Exception as e:
		print(f"Error processing file {file_path}: {e}")
	else:
		print(f"rule {index} exec succeeded on {file_path}")
