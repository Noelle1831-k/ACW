import ast
import hashlib
import os
import shutil
import subprocess
import time
from typing import Tuple
import json
import math
import folder_list
from one_rule_format import tab_convert_process, reorder_process
import concurrent.futures
from run_pep8_test import process_files_in_folder

def process(folder_path):
    abs_folder_path = os.path.abspath(folder_path)
    abs_config_path = os.path.abspath('.sourcery.yaml')

    command_str = f'sourcery review --config "{abs_config_path}" --fix "{abs_folder_path}"'

    try:
        result = subprocess.run(command_str, shell=True, text=True)

        if result.returncode != 0:
            print(f"[Error] Sourcery execution failed (Code {result.returncode}): {abs_folder_path}")
    except Exception as e:
        print(f"[Exception] Subprocess execution error: {e}")

    if os.path.exists(abs_folder_path):
        for root, dirs, files in os.walk(abs_folder_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        for index in [36, 37, 38, 39]:
                            reorder_process(index, file_path)
                        tab_convert_process(45, file_path)
                    except Exception as e:
                        print(f"[Warning] reorder_process error {file_path}: {e}")
        process_files_in_folder(folder_path)

def copy_folder_force(src, dst):
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)

def compare_dir_hash_counts(dir1: str, dir2: str) -> Tuple[int, int]:
    def file_hash(path: str) -> str:
        h = hashlib.sha256()
        try:
            with open(path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    h.update(chunk)
            return h.hexdigest()
        except FileNotFoundError:
            return "missing"
        except Exception:
            return "error"

    if not os.path.exists(dir1) or not os.path.exists(dir2):
        return 0, 0

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

        h1 = file_hash(path1)
        h2 = file_hash(path2)

        if h1 == h2:
            same_count += 1
        else:
            diff_count += 1

    return same_count, diff_count

def calculate_z_score(changed_count, total_count):
    if total_count == 0:
        return 0.0
    p = 0.5
    mu = total_count * p
    sigma = math.sqrt(total_count * p * (1 - p))
    if sigma == 0:
        return 0.0
    z_score = (changed_count - mu) / sigma
    return z_score

def process_single_project(project_name, projects_root_folder, backup_root, z_threshold):
    project_path = os.path.join(projects_root_folder, project_name)
    backup_path = os.path.join(backup_root, project_name)

    print(f"--> Start processing: {project_name}")

    try:
        copy_folder_force(project_path, backup_path)

        process(project_path)

        same_count, diff_count = compare_dir_hash_counts(project_path, backup_path)
        total_files = same_count + diff_count

        z_val = calculate_z_score(diff_count, total_files)

        is_generated = z_val > z_threshold
        label = "Generated" if is_generated else "Human-Written"

        print(f"✅ Completed: {project_name} | Changed: {diff_count}/{total_files} | Z: {z_val:.2f} | Result: {label}")

        return {
            "project_name": project_name,
            "total_files": total_files,
            "changed_files": diff_count,
            "unchanged_files": same_count,
            "z_score": round(z_val, 4),
            "threshold": z_threshold,
            "prediction": label
        }

    except Exception as e:
        print(f"❌ Processing failed {project_name}: {e}")
        return None

def process_project_mode(projects_root_folder, z_threshold=1.96, max_workers=4):
    project_results = []

    backup_root = projects_root_folder + "_backup"
    if not os.path.exists(backup_root):
        os.makedirs(backup_root)

    sub_projects = [
        f for f in os.listdir(projects_root_folder)
        if os.path.isdir(os.path.join(projects_root_folder, f))
    ]

    print(f"--- Starting multi-threaded detection (Workers: {max_workers}), Total {len(sub_projects)} projects ---")
    print(f"--- Please check console for Sourcery error messages ---")

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for p_name in sub_projects:
            futures.append(executor.submit(
                process_single_project,
                p_name,
                projects_root_folder,
                backup_root,
                z_threshold
            ))

        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            if res:
                project_results.append(res)

    return project_results

if __name__ == '__main__':
    RUN_PROJECT_MODE = True

    MAX_WORKERS = 32

    if not os.path.exists('.sourcery.yaml'):
        print("⚠️ Warning: .sourcery.yaml config file not found in current directory, Sourcery may not run correctly!")

    if RUN_PROJECT_MODE:
        TARGET_PROJECTS_DIR = 'Python_func'
        Z_SCORE_THRESHOLD = 1.645

        if os.path.exists(TARGET_PROJECTS_DIR):
            final_results = process_project_mode(TARGET_PROJECTS_DIR, Z_SCORE_THRESHOLD, MAX_WORKERS)

            with open('project_detection_results.json', 'w', encoding='utf-8') as f:
                json.dump(final_results, f, ensure_ascii=False, indent=4)
            print("\nAll tasks completed, results saved.")
        else:
            print(f"Error: Directory not found {TARGET_PROJECTS_DIR}")
