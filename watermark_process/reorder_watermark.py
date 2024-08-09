import os
import ast
import hashlib
import os
import subprocess

import astor
import autopep8

from folder_list import folder_paths


def get_sorted_hash(value):
    sorted_value = ''.join(sorted(value))
    return hashlib.sha256(sorted_value.encode()).hexdigest()


# Rule 36
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
                    with open(file_path, 'w') as file:
                        new_content = astor.to_source(tree)
                        new_content = '\n'.join(line for line in new_content.split('\n') if line.strip())
                        file.write(new_content)
                        print("write done")
                    return 1


# Rule 37
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
                    with open(file_path, 'w') as file:
                        new_content = astor.to_source(tree)
                        new_content = '\n'.join(line for line in new_content.split('\n') if line.strip())
                        file.write(new_content)
                        print("write done")
                    return 1


# Rule 38
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
                            with open(file_path, 'w') as file:
                                new_content = astor.to_source(tree)
                                new_content = '\n'.join(line for line in new_content.split('\n') if line.strip())
                                file.write(new_content)
                                print("write done")
                            return 1


# Rule 39
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
                            with open(file_path, 'w') as file:
                                new_content = astor.to_source(tree)
                                new_content = '\n'.join(line for line in new_content.split('\n') if line.strip())
                                file.write(new_content)
                                print("write done")
                            return 1



if __name__ == "__main__":
    C = [
        "_1",
        "_2",
        "_3",
        "_4",
        "_5",
        "_6",
        "_over6",
    ]
    # Rule 1-35

    for folder_path in folder_paths:
        for c in C:
            new_folder_path = os.path.join(folder_path, folder_path[2:] + c)
            python_files = [f for f in os.listdir(new_folder_path) if f.endswith('.py')]

            for file in python_files:
                file_path = os.path.join(new_folder_path, file)
                try:
                    with open(file_path, 'r') as file:
                        content = file.read()
                        lines = content.split('\n')
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        transform_operations_add(node, lines, file_path)
                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")
            for file in python_files:
                file_path = os.path.join(new_folder_path, file)
                try:
                    with open(file_path, 'r') as file:
                        content = file.read()
                        lines = content.split('\n')
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        transform_operations_mult(node, lines, file_path)
                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")
            for file in python_files:
                file_path = os.path.join(new_folder_path, file)
                try:
                    with open(file_path, 'r') as file:
                        content = file.read()
                        lines = content.split('\n')
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        transform_comparison_LG(node, lines, file_path)
                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")
            for file in python_files:
                file_path = os.path.join(new_folder_path, file)
                try:
                    with open(file_path, 'r') as file:
                        content = file.read()
                        lines = content.split('\n')
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        transform_comparison_LGE(node, lines, file_path)
                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")