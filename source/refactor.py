import argparse
import difflib
import os
import shutil
import subprocess
import time
import hashlib
import json
import logging
import random
import threading
import uuid
import concurrent.futures
from dataclasses import dataclass, asdict
from typing import List, Tuple, Optional, Dict, Any

import folder_list
import refact_list
from one_rule_format import reorder_process, tab_convert_process
from formatting_pep8 import apply_pep8_rule


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


@dataclass
class ExperimentMetrics:
	folder_path: str
	is_generated: bool
	match_count: int = 0
	diff_count: int = 0
	time_cost: float = 0.0
	tp: int = 0
	fp: int = 0
	tn: int = 0
	fn: int = 0
	
	def calculate_confusion_matrix(self):
		if self.is_generated:
			self.tp = self.match_count
			self.fn = self.diff_count
		else:
			self.tn = self.diff_count
			self.fp = self.match_count
	
	def to_dict(self):
		self.calculate_confusion_matrix()
		return asdict(self)


@dataclass
class IdempotenceMetrics:
	folder_path: str
	rule_id: str
	rounds_details: List[Dict[str, Any]]
	is_converged: bool = False
	
	def to_dict(self):
		return asdict(self)


class WatermarkInjector:
	def __init__(self, num_transforms: int = 10, seed: Optional[int] = None, random_rules: Optional[bool] = False,
	             batch: int = 5):
		self.num_transforms = num_transforms
		self.seed = seed
		self.batch = batch
		self.rule_pool = list(range(1, 46))
		for _ in [5, 10]:
			if _ in self.rule_pool:
				self.rule_pool.remove(_)
		
		if self.seed is not None:
			random.seed(self.seed)
		self.selected_rules = random.sample(self.rule_pool, min(self.num_transforms, len(self.rule_pool)))
		self.selected_rules.sort()
		if random_rules:
			random.shuffle(self.selected_rules)
	
	def apply(self, target_folder: str):
		self.apply_specific_rules(target_folder, self.selected_rules)
	
	def apply_specific_rules(self, target_folder: str, rules: List[int]):
		if not os.path.exists(target_folder):
			logging.error(f"Folder does not exist: {target_folder}")
			return
		
		sourcery_rule_ids = [r for r in rules if 1 <= r <= 35]
		custom_rule_ids_1 = [r for r in rules if 45 >= r > 35]
		
		if sourcery_rule_ids:
			self._apply_sourcery_rules(target_folder, sourcery_rule_ids)
		
		if custom_rule_ids_1:
			all_files = []
			for root, _, files in os.walk(target_folder):
				for file in files:
					if file.endswith('.py'):
						all_files.append(os.path.join(root, file))
			
			if all_files:
				with concurrent.futures.ThreadPoolExecutor(max_workers=self.batch) as executor:
					futures = [
						executor.submit(self._apply_custom_rules_to_file, file_path, custom_rule_ids_1)
						for file_path in all_files
					]
					for future in concurrent.futures.as_completed(futures):
						try:
							future.result()
						except Exception as e:
							logging.error(f"Error processing file: {e}")
	
	def _apply_sourcery_rules(self, target_folder: str, rule_ids: List[int]):
		rule_names = []
		for rid in rule_ids:
			try:
				if rid - 1 < len(refact_list.refactoring_list):
					rule_names.append(refact_list.refactoring_list[rid - 1])
			except Exception:
				pass
		
		if not rule_names:
			return
		
		config_content = "version: '1'\nrule_settings:\n  enable:\n"
		for name in rule_names:
			config_content += f"  - {name}\n"
		
		unique_config_path = f'.sourcery_temp_{uuid.uuid4().hex}.yaml'
		
		try:
			with open(unique_config_path, 'w', encoding='utf-8') as f:
				f.write(config_content)
			
			command = ['sourcery', 'review', '--config', unique_config_path, '--fix', target_folder]
			cmd_str = ' '.join(command)
			subprocess.run(cmd_str, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
		finally:
			if os.path.exists(unique_config_path):
				try:
					os.remove(unique_config_path)
				except OSError:
					pass
	
	def _apply_custom_rules_to_file(self, file_path: str, rule_ids: List[int]):
		for rule_id in rule_ids:
			self._dispatch_custom_rule(file_path, rule_id)
	
	def _dispatch_custom_rule(self, file_path: str, rule_id: int):
		try:
			if 36 <= rule_id <= 39:
				reorder_process(rule_id, file_path)
			elif 40 <= rule_id <= 44:
				apply_pep8_rule(rule_id, file_path)
			elif rule_id == 45:
				tab_convert_process(45, file_path)
		except Exception as e:
			logging.error(f"Rule {rule_id} error on {file_path}: {e}")


class ExperimentEvaluator:
	@staticmethod
	def calculate_hash(file_path: str) -> str:
		h = hashlib.sha256()
		try:
			with open(file_path, 'rb') as f:
				for chunk in iter(lambda: f.read(8192), b''):
					h.update(chunk)
		except IOError:
			return ""
		return h.hexdigest()
	
	def compare_directories(self, dir_original: str, dir_modified: str) -> Tuple[int, int]:
		def get_rel_paths(d):
			return {
				os.path.relpath(os.path.join(r, f), d)
				for r, _, files in os.walk(d) for f in files
			}
		
		rels_orig = get_rel_paths(dir_original)
		rels_mod = get_rel_paths(dir_modified)
		common_files = rels_orig & rels_mod
		
		same = 0
		diff = 0
		for rel in common_files:
			p1 = os.path.join(dir_original, rel)
			p2 = os.path.join(dir_modified, rel)
			
			if self.calculate_hash(p1) == self.calculate_hash(p2):
				same += 1
			else:
				diff += 1
		
		return same, diff


class WatermarkExperimentRunner:
	def __init__(self, output_file: str = 'output.json', num_transforms: int = None, seed: int = None,
	             random_rules: bool = False, batch: int = 5):
		self.injector = WatermarkInjector(num_transforms=num_transforms, random_rules=random_rules, seed=seed,
		                                  batch=batch)
		self.evaluator = ExperimentEvaluator()
		self.output_file = output_file
		self.results: List[ExperimentMetrics] = []
		self.idempotence_results: List[IdempotenceMetrics] = []
		self.chain_results: List[Dict] = []
		self.lock = threading.Lock()
	
	def _backup_folder(self, src: str, prefix: str) -> str:
		dirname = os.path.basename(os.path.normpath(src))
		backup_dst = os.path.join(prefix, dirname)
		if os.path.exists(backup_dst):
			shutil.rmtree(backup_dst)
		os.makedirs(os.path.dirname(backup_dst), exist_ok=True)
		shutil.copytree(src, backup_dst)
		return backup_dst
	
	def run_single_folder(self, folder_path: str):
		start_time = time.time()
		logging.info(f"Processing Detection Test: {folder_path}")
		is_generated = folder_path.startswith('G') or "Generated" in folder_path
		
		unique_id = uuid.uuid4().hex[:8]
		temp_work_dir = self._backup_folder(folder_path, f"temp_work_{unique_id}")
		
		snapshot_path = None
		match_count = 0
		diff_count = 0
		
		try:
			if is_generated:
				self.injector.apply(temp_work_dir)
				snapshot_path = self._backup_folder(temp_work_dir, f"temp_snap_{unique_id}")
				self.injector.apply(snapshot_path)
				match_count, diff_count = self.evaluator.compare_directories(temp_work_dir, snapshot_path)
			else:
				snapshot_path = self._backup_folder(temp_work_dir, f"temp_snap_{unique_id}")
				self.injector.apply(temp_work_dir)
				match_count, diff_count = self.evaluator.compare_directories(snapshot_path, temp_work_dir)
		
		finally:
			if os.path.exists(temp_work_dir):
				shutil.rmtree(temp_work_dir)
			if snapshot_path and os.path.exists(snapshot_path):
				shutil.rmtree(snapshot_path)
		
		time_cost = time.time() - start_time
		metric = ExperimentMetrics(
			folder_path=folder_path,
			is_generated=is_generated,
			match_count=match_count,
			diff_count=diff_count,
			time_cost=time_cost
		)
		
		with self.lock:
			self.results.append(metric)
	
	def save_detection_results(self):
		if not self.results:
			logging.warning("No detection results to save.")
			return
		
		data = [r.to_dict() for r in self.results]
		try:
			with open(self.output_file, 'w', encoding='utf-8') as f:
				json.dump(data, f, ensure_ascii=False, indent=4)
			logging.info(f"✅ Detection results saved to {self.output_file}")
		except Exception as e:
			logging.error(f"❌ Failed to save detection results: {e}")
	
	def run_rule_scan(self, folder_list_source):
		logging.info("🚀 Starting Full Rule Scan (1-45) for Idempotence with Multi-threading...")
		max_workers = 1
		
		with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
			future_to_rule = {
				executor.submit(self._process_single_rule_task, rule_id, folder_list_source): rule_id
				for rule_id in [1, 4, 5, 6, 11, 34, 36, 37, 39]
			}
			
			for future in concurrent.futures.as_completed(future_to_rule):
				rule_id = future_to_rule[future]
				try:
					future.result()
					logging.info(f"✅ Rule {rule_id} scan completed.")
				except Exception as exc:
					logging.error(f"❌ Rule {rule_id} generated an exception: {exc}")
		
		self.save_idempotence_results()
	
	def _process_single_rule_task(self, rule_id: int, folder_list_source: List[str]):
		for folder in folder_list_source:
			self._run_idempotence_test_logic(folder, specific_rules=[rule_id])
	
	def run_batch_random_idempotence(self, folder_list_source):
		for folder in folder_list_source:
			self._run_idempotence_test_logic(folder, specific_rules=None)
		self.save_idempotence_results()
	
	def _run_idempotence_test_logic(self, folder_path: str, specific_rules: List[int] = None):
		rule_label = f"Rule-{specific_rules[0]}" if specific_rules and len(specific_rules) == 1 else "Random-Set"
		unique_suffix = uuid.uuid4().hex[:6]
		
		work_dir = self._backup_folder(folder_path, f"temp_work_{rule_label}_{unique_suffix}")
		
		rounds_stats = []
		max_rounds = 5
		
		try:
			for r in range(1, max_rounds + 1):
				pre_apply_snapshot = self._backup_folder(work_dir, f"temp_snap_r{r}_{unique_suffix}")
				
				try:
					if specific_rules:
						self.injector.apply_specific_rules(work_dir, specific_rules)
					else:
						self.injector.apply(work_dir)
					
					same, diff = self.evaluator.compare_directories(pre_apply_snapshot, work_dir)
					
					total = same + diff
					convergence_rate = (same / total) if total > 0 else 1.0
					
					round_data = {
						"round": r,
						"total_files": total,
						"unchanged": same,
						"changed": diff,
						"convergence_rate": convergence_rate
					}
					if r > 1:
						rounds_stats.append(round_data)
					
					if diff > 0:
						logging.info(f"   [{rule_label}] Round {r}: Changed {diff} files.")
				
				finally:
					if os.path.exists(pre_apply_snapshot):
						shutil.rmtree(pre_apply_snapshot)
			
			is_converged = (rounds_stats[-1]['changed'] == 0)
			
			metric = IdempotenceMetrics(
				folder_path=folder_path,
				rule_id=rule_label,
				rounds_details=rounds_stats,
				is_converged=is_converged
			)
			
			with self.lock:
				self.idempotence_results.append(metric)
		
		finally:
			if os.path.exists(work_dir):
				shutil.rmtree(work_dir)
	
	def save_idempotence_results(self):
		filename = self.output_file if self.output_file != 'output.json' else 'idempotence_scan_5rounds.json'
		data = sorted([r.to_dict() for r in self.idempotence_results], key=lambda x: str(x['rule_id']))
		try:
			with open(filename, 'w', encoding='utf-8') as f:
				json.dump(data, f, ensure_ascii=False, indent=4)
			logging.info(f"Idempotence results (5-Rounds) saved to {filename}")
		except Exception as e:
			logging.error(f"Failed to save idempotence results: {e}")
	
	def run_chained_experiment(self, folder_path: str, chain_length: int = 3):
		logging.info(f"🔗 Starting Chain Experiment (Length={chain_length}) on {folder_path}")
		unique_id = uuid.uuid4().hex[:8]
		current_code_dir = self._backup_folder(folder_path, f"chain_work_{unique_id}")
		
		history_rule_lists = []
		chain_data = {
			"folder": folder_path,
			"steps": []
		}
		
		try:
			for step_i in range(1, chain_length + 1):
				step_info = {"step": step_i, "rule_list": [], "self_tpr": {}, "history_tpr": []}
				
				available_rules = self.injector.rule_pool
				sample_size = len(available_rules) // 2
				current_rules = random.sample(available_rules, sample_size)
				current_rules.sort()
				step_info["rule_list"] = current_rules
				history_rule_lists.append(current_rules)
				
				self.injector.apply_specific_rules(current_code_dir, current_rules)
				
				backup_for_self_check = self._backup_folder(current_code_dir, f"chain_temp_self_{unique_id}")
				try:
					self.injector.apply_specific_rules(backup_for_self_check, current_rules)
					s_same, s_diff = self.evaluator.compare_directories(current_code_dir, backup_for_self_check)
					total = s_same + s_diff
					step_info["self_tpr"] = {
						"match": s_same, "diff": s_diff,
						"rate": s_same / total if total > 0 else 1.0
					}
				finally:
					if os.path.exists(backup_for_self_check): shutil.rmtree(backup_for_self_check)
				
				for hist_idx, hist_rules in enumerate(history_rule_lists[:-1]):
					hist_step_num = hist_idx + 1
					backup_for_hist_check = self._backup_folder(current_code_dir, f"chain_temp_hist_{unique_id}")
					try:
						self.injector.apply_specific_rules(backup_for_hist_check, hist_rules)
						h_same, h_diff = self.evaluator.compare_directories(current_code_dir, backup_for_hist_check)
						total = h_same + h_diff
						step_info["history_tpr"].append({
							"checked_against_step": hist_step_num,
							"match": h_same, "diff": h_diff,
							"rate": h_same / total if total > 0 else 1.0
						})
					finally:
						if os.path.exists(backup_for_hist_check): shutil.rmtree(backup_for_hist_check)
				
				chain_data["steps"].append(step_info)
		
		finally:
			if os.path.exists(current_code_dir):
				shutil.rmtree(current_code_dir)
		
		with self.lock:
			self.chain_results.append(chain_data)
			self._save_chain_results()
	
	def _save_chain_results(self):
		filename = self.output_file if self.output_file != 'output.json' else f'chain_results_{int(time.time())}.json'
		try:
			with open(filename, 'w', encoding='utf-8') as f:
				json.dump(self.chain_results, f, ensure_ascii=False, indent=4)
		except Exception as e:
			logging.error(f"Failed to save chain results: {e}")


def get_target_folders(args_target):
	if args_target:
		return [args_target]
	elif hasattr(folder_list, 'folder_paths') and folder_list.folder_paths:
		return folder_list.folder_paths
	else:
		logging.error("No target folders found. Provide --target or check folder_list.py")
		return []


def main():
	parser = argparse.ArgumentParser(description="Watermark Experiment Automation Script")
	subparsers = parser.add_subparsers(dest='mode', help='Experiment Mode', required=True)
	
	parent_parser = argparse.ArgumentParser(add_help=False)
	parent_parser.add_argument('--seed', type=int, default=42, help='Random seed (default: 42)')
	parent_parser.add_argument('--output', type=str, default='output.json', help='Output JSON filename')
	parent_parser.add_argument('--batch', type=int, default=5, help='Worker batch size (default: 5)')
	parent_parser.add_argument('--target', type=str, help='Specific target folder path (overrides folder_list.py)')
	
	parser_detect = subparsers.add_parser('detect', parents=[parent_parser],
	                                      help='Run basic watermark detection/injection test')
	parser_detect.add_argument('--transforms', type=int, default=46, help='Number of transforms to apply')
	
	parser_idem = subparsers.add_parser('idempotence', parents=[parent_parser],
	                                    help='Run idempotence (convergence) analysis')
	parser_idem.add_argument('--type', choices=['scan', 'random'], default='scan',
	                         help='Type: "scan" (specific rules) or "random" (random sets)')
	
	parser_chain = subparsers.add_parser('chain', parents=[parent_parser], help='Run chained watermarking experiment')
	parser_chain.add_argument('--length', type=int, default=3, help='Chain length (default: 3)')
	
	args = parser.parse_args()
	
	targets = get_target_folders(args.target)
	if not targets:
		return
	
	runner = WatermarkExperimentRunner(
		output_file=args.output,
		num_transforms=getattr(args, 'transforms', 46),
		seed=args.seed,
		random_rules=True,
		batch=args.batch
	)
	
	if args.mode == 'detect':
		logging.info("--- Mode: Detection Test ---")
		for folder in targets:
			runner.run_single_folder(folder)
		runner.save_detection_results()
	
	elif args.mode == 'idempotence':
		logging.info(f"--- Mode: Idempotence ({args.type}) ---")
		if args.type == 'scan':
			runner.run_rule_scan(targets)
		else:
			runner.run_batch_random_idempotence(targets)
	
	elif args.mode == 'chain':
		logging.info(f"--- Mode: Chain Experiment (Length: {args.length}) ---")
		for folder in targets:
			runner.run_chained_experiment(folder, chain_length=args.length)


if __name__ == '__main__':
	main()

