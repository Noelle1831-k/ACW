import os
import json
import random
from pathlib import Path
from folder_list import folder_paths


def create_jsonl_dataset(
		transformed_folder,
		original_folder,
		train_output_path,
		val_output_path,
		split_ratio=0.9,
		swap_ratio=0.5,
		file_extension=".py"
):
	data_samples = []
	
	trans_path = Path(transformed_folder)
	orig_path = Path(original_folder)
	
	if not trans_path.exists() or not orig_path.exists():
		print(f"Error: Folder paths do not exist. Please check: \n{transformed_folder}\n{original_folder}")
		return
	
	files = [f for f in os.listdir(trans_path) if f.endswith(file_extension)]
	print(f"Scanned {len(files)} files, starting processing...")
	
	matched_count = 0
	missing_count = 0
	
	for filename in files:
		trans_file_path = trans_path / filename
		orig_file_path = orig_path / filename
		
		if orig_file_path.exists():
			try:
				with open(trans_file_path, 'r', encoding='utf-8', errors='ignore') as f:
					transformed_code = f.read()
				
				with open(orig_file_path, 'r', encoding='utf-8', errors='ignore') as f:
					original_code = f.read()
				
				entry = {
					"transformed": transformed_code,
					"original": original_code
				}
				data_samples.append(entry)
				matched_count += 1
			except Exception as e:
				print(f"Error reading file {filename}: {e}")
		else:
			missing_count += 1
	
	print(f"Processing complete. Matched: {matched_count}, Missing: {missing_count}")
	
	random.seed(42)
	
	split_index = int(len(data_samples) * split_ratio)
	train_data = data_samples[:split_index]
	val_data = data_samples[split_index:]
	
	print(f"Performing random swap on training set (Probability: {swap_ratio})...")
	swap_count = 0
	for data in train_data:
		if random.random() < swap_ratio:
			data['transformed'], data['original'] = data['original'], data['transformed']
			swap_count += 1
	
	print(f"Swap complete: {swap_count} out of {len(train_data)} items had Input/Output swapped.")
	for data in val_data:
		data['transformed'] = 'Transform the python code to original code: ' + data['transformed']
	
	def write_jsonl(data, path):
		with open(path, 'w', encoding='utf-8') as f:
			for entry in data:
				f.write(json.dumps(entry, ensure_ascii=False) + '\n')
	
	print(f"Writing training set ({len(train_data)} items) to {train_output_path} ...")
	write_jsonl(train_data, train_output_path)
	
	print(f"Writing validation set ({len(val_data)} items) to {val_output_path} ...")
	write_jsonl(val_data, val_output_path)
	
	print("Dataset creation complete!")


if __name__ == "__main__":
	for folder_path in folder_paths:
		FOLDER_A = folder_path
		FOLDER_B = "copy_H/" + folder_path
		
		TRAIN_OUT = FOLDER_A.replace('/', '_') + '_' + "train_data.jsonl"
		VAL_OUT = "val_data.jsonl"
		
		create_jsonl_dataset(
			transformed_folder=FOLDER_A,
			original_folder=FOLDER_B,
			train_output_path=TRAIN_OUT,
			val_output_path=VAL_OUT,
			split_ratio=1,
			swap_ratio=0
		)
