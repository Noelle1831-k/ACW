import os

def rename_files_in_directory(directory):
    for filename in os.listdir(directory):
        if '-' in filename and filename.endswith('.py'):
            new_filename = filename.split('-')[0] + '.py'
            old_filepath = os.path.join(directory, filename)
            new_filepath = os.path.join(directory, new_filename)
            os.rename(old_filepath, new_filepath)
            print(f"Renamed: {filename} to {new_filename}")

# 指定目录
directory_path = 'G_be/MBPP_Starcoder_G'

rename_files_in_directory(directory_path)