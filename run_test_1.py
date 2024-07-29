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
def transform_operations_add(node, lines, file_path,tree):
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


# Rule 37
def transform_operations_mult(node, lines, file_path,tree):
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


# Rule 38
def transform_comparison_LG(node, lines, file_path,tree):
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


# Rule 39
def transform_comparison_LGE(node, lines, file_path,tree):
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