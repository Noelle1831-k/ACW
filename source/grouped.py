import os
import sys
import shutil
from collections import defaultdict

def count_and_move_by_line_count(directory):
    buckets = defaultdict(int)
    bucket_names = ["1-5", "5-10", "10-15", "15-20", "20-25", "25-30", "30-35", "35-40", "40-45", "45-50", "others"]
    for b in bucket_names:
        os.makedirs(os.path.join(directory, b), exist_ok=True)
    for root, dirs, files in os.walk(directory):
        if os.path.abspath(root) in {os.path.abspath(os.path.join(directory, b)) for b in bucket_names}:
            continue
        for fname in files:
            filepath = os.path.join(root, fname)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    line_count = sum(1 for _ in f)
                if 1 <= line_count < 5:
                    bucket = "1-5"
                elif 5 <= line_count < 10:
                    bucket = "5-10"
                elif 10 <= line_count < 15:
                    bucket = "10-15"
                elif 15 <= line_count < 20:
                    bucket = "15-20"
                elif 20 <= line_count < 25:
                    bucket = "20-25"
                elif 25 <= line_count < 30:
                    bucket = "25-30"
                elif 30 <= line_count < 35:
                    bucket = "30-35"
                elif 35 <= line_count < 40:
                    bucket = "35-40"
                elif 40 <= line_count < 45:
                    bucket = "40-45"
                elif 45 <= line_count < 50:
                    bucket = "45-50"
                else:
                    bucket = "others"
                dest_dir = os.path.join(directory, bucket)
                dest_path = os.path.join(dest_dir, fname)
                base, ext = os.path.splitext(fname)
                counter = 1
                while os.path.exists(dest_path):
                    dest_path = os.path.join(dest_dir, f"{base}_{counter}{ext}")
                    counter += 1
                shutil.move(filepath, dest_path)

                buckets[bucket] += 1
            except Exception as e:
                print(f"Error processing {filepath}: {e}")
    return buckets

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python move_by_line_count.py <directory_path>")
        sys.exit(1)
    root_dir = sys.argv[1]
    distribution = count_and_move_by_line_count(root_dir)
    for bucket in ["1-5", "5-10", "10-15", "15-20", "20-25", "25-30", "30-35", "35-40", "40-45", "45-50", "others"]:
        print(f"{bucket} lines: {distribution.get(bucket, 0)} files")
