import ast
import hashlib
import os
import astor

from base import folder_list


def get_sorted_hash(value):
	sorted_value = ''.join(sorted(value))
	return hashlib.sha256(sorted_value.encode()).hexdigest()


def transform_operations_add(node, lines, file_path):
	if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
		left_var = node.left.id if isinstance(node.left, ast.Name) else None
		right_var = node.right.id if isinstance(node.right, ast.Name) else None

		if left_var and right_var:
			hash_left = get_sorted_hash(left_var)
			hash_right = get_sorted_hash(right_var)

			original_code = astor.to_source(node)

			if hash_left < hash_right:
				node.left, node.right = node.right, node.left

				transformed_code = astor.to_source(node).strip()

				if original_code.strip() != transformed_code:
					new_file_path = file_path[:-3] + '-36.py'
					# print(new_file_path)
					os.rename(file_path, new_file_path)
					return 1


def transform_operations_mult(node, lines, file_path):
	if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mult):
		left_var = node.left.id if isinstance(node.left, ast.Name) else None
		right_var = node.right.id if isinstance(node.right, ast.Name) else None

		if left_var and right_var:
			hash_left = get_sorted_hash(left_var)
			hash_right = get_sorted_hash(right_var)

			original_code = astor.to_source(node)

			if hash_left < hash_right:
				node.left, node.right = node.right, node.left

				transformed_code = astor.to_source(node).strip()

				if original_code.strip() != transformed_code:
					new_file_path = file_path[:-3] + '-37.py'
					# print(new_file_path)
					os.rename(file_path, new_file_path)
					return 1


def transform_comparison_LG(node, lines, file_path):
	if isinstance(node, ast.Compare):
		for op in node.ops:
			if isinstance(op, (ast.Gt, ast.Lt)):
				left_var = node.left.id if isinstance(node.left, ast.Name) else None
				right_var = node.comparators[0].id if isinstance(node.comparators[0], ast.Name) else None

				if left_var and right_var:
					hash_left = get_sorted_hash(left_var)
					hash_right = get_sorted_hash(right_var)

					original_code = astor.to_source(node)

					if hash_left < hash_right:
						if isinstance(op, ast.Gt):
							node.left, node.comparators[0] = node.comparators[0], node.left
							node.ops[0] = ast.Lt()
						elif isinstance(op, ast.Lt):
							node.left, node.comparators[0] = node.comparators[0], node.left
							node.ops[0] = ast.Gt()

						transformed_code = astor.to_source(node).strip()

						if original_code.strip() != transformed_code:
							new_file_path = file_path[:-3] + '-38.py'
							# print(new_file_path)
							os.rename(file_path, new_file_path)
							return 1


def transform_comparison_LGE(node, lines, file_path):
	if isinstance(node, ast.Compare):
		for op in node.ops:
			if isinstance(op, (ast.GtE, ast.LtE)):
				left_var = node.left.id if isinstance(node.left, ast.Name) else None
				right_var = node.comparators[0].id if isinstance(node.comparators[0], ast.Name) else None

				if left_var and right_var:
					hash_left = get_sorted_hash(left_var)
					hash_right = get_sorted_hash(right_var)

					original_code = astor.to_source(node)

					if hash_left < hash_right:
						if isinstance(op, ast.GtE):
							node.left, node.comparators[0] = node.comparators[0], node.left
							node.ops[0] = ast.LtE()
						elif isinstance(op, ast.LtE):
							node.left, node.comparators[0] = node.comparators[0], node.left
							node.ops[0] = ast.GtE()

						transformed_code = astor.to_source(node).strip()

						if original_code.strip() != transformed_code:
							new_file_path = file_path[:-3] + '-39.py'
							# print(new_file_path)
							os.rename(file_path, new_file_path)
							return 1


if __name__ == "__main__":
	for folder_path in folder_list.folder_paths:

		python_files = [f for f in os.listdir(folder_path) if f.endswith('.py')]
		for file in python_files:
			file_path = os.path.join(folder_path, file)
			try:
				with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
					original_code = f.read()
					lines = original_code.split('\n')
				tree = ast.parse(original_code,type_comments=True)
				# rule 36
				for node in ast.walk(tree):
					flag = transform_operations_add(node, lines, file_path)
					if flag == 1:
						break
			except Exception as e:
				print(f"Error processing file {file_path}: {e}")
	for folder_path in folder_list.folder_paths:

		python_files = [f for f in os.listdir(folder_path) if f.endswith('.py')]

		for file in python_files:
			file_path = os.path.join(folder_path, file)
			try:
				with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
					original_code = f.read()
					lines = original_code.split('\n')
				tree = ast.parse(original_code)
				# rule 37
				for node in ast.walk(tree):
					flag = transform_operations_mult(node, lines, file_path)
					if flag == 1:
						break
			except Exception as e:
				print(f"Error processing file {file_path}: {e}")
	for folder_path in folder_list.folder_paths:
		python_files = [f for f in os.listdir(folder_path) if f.endswith('.py')]

		for file in python_files:
			file_path = os.path.join(folder_path, file)
			try:
				with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
					original_code = f.read()
					lines = original_code.split('\n')
				tree = ast.parse(original_code)
				# rule 38
				for node in ast.walk(tree):
					flag = transform_comparison_LG(node, lines, file_path)
					if flag == 1:
						break
			except Exception as e:
				print(f"Error processing file {file_path}: {e}")

	for folder_path in folder_list.folder_paths:
		python_files = [f for f in os.listdir(folder_path) if f.endswith('.py')]
		for file in python_files:
			file_path = os.path.join(folder_path, file)
			try:
				with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
					original_code = f.read()
					lines = original_code.split('\n')
				tree = ast.parse(original_code)
				# rule 39
				for node in ast.walk(tree):
					flag = transform_comparison_LGE(node, lines, file_path)
					if flag == 1:
						break
			except Exception as e:
				print(f"Error processing file {file_path}: {e}")
