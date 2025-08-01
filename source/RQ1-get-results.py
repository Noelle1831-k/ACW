import hashlib
import os
import shutil
import subprocess
from typing import Tuple
import json
import folder_list
from one_rule_format import tab_convert_process, reorder_process
from run_pep8_test import process_files_in_folder


def process(folder_path):
    command = [
        'sourcery',
        'review',
        '--config',
        '.sourcery.yaml',
        '--fix',
        folder_path
    ]
    command_str = ' '.join(command)
    result = subprocess.run(command_str, shell=True, text=True)
    if result.returncode == 0:
        print(f"Command executed successfully.")
    new_folder_path = folder_path
    python_files = [f for f in os.listdir(new_folder_path) if f.endswith('.py')]
    for file in python_files:
        file_path = os.path.join(new_folder_path, file)
        for index in [36, 37, 38, 39]:
            reorder_process(index, file_path)
    overall_results = []
    folder_results = process_files_in_folder(folder_path)
    overall_results.extend(folder_results)
    for result in overall_results:
        print(result)
    for file in python_files:
        file_path = os.path.join(new_folder_path, file)
        tab_convert_process(45, file_path)


def copy_folder_force(src, dst):
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    print(f"Copy {src} to {dst}")


def compare_dir_hash_counts(dir1: str, dir2: str) -> Tuple[int, int]:
    def file_hash(path: str) -> str:
        h = hashlib.sha256()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                h.update(chunk)
        return h.hexdigest()
    rels1 = {
        os.path.relpath(os.path.join(r, f), dir1)
        for r, _, files in os.walk(dir1) for f in files
    }
    rels2 = {
        os.path.relpath(os.path.join(r, f), dir2)
        for r, _, files in os.walk(dir2) for f in files
    }
    common = rels1 & rels2
    same_count = 0
    diff_count = 0
    for rel in common:
        path1 = os.path.join(dir1, rel)
        path2 = os.path.join(dir2, rel)
        if file_hash(path1) == file_hash(path2):
            same_count += 1
        else:
            diff_count += 1
    return same_count, diff_count


def calu_result(TP, FP, TN, FN):
    TPR = TP / (TP + FN)
    FPR = FP / (FP + TN)
    ACC = (TP + TN) / (TP + TN + FP + FN)
    return TPR, FPR, ACC


if __name__ == '__main__':
    result = []
    for folder_path_all in folder_list.folder_paths:
        folder_path = folder_path_all
        if folder_path.startswith('G'):
            process(folder_path)
            copy_folder_force(folder_path, os.path.join('copy_G', folder_path))
            process(folder_path)
            TP, FP = compare_dir_hash_counts(folder_path, os.path.join('copy_G', folder_path))
            result_G = [TP, FP, folder_path]
            print(result_G)
            result.append(result_G)
        else:
            copy_folder_force(folder_path, os.path.join('copy_H', folder_path))
            process(folder_path)
            FN, TN = compare_dir_hash_counts(folder_path, os.path.join('copy_H', folder_path))
            result_H = [FN, TN, folder_path]
            print(result_H)
            result.append(result_H)
    print(result)
    with open('output.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
    
    print("Save results to output.json")
