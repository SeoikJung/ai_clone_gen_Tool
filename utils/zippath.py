import os
import shutil
import zipfile
from datetime import datetime

def clean_zip_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    else:
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isfile(item_path) and item_path.endswith('.zip'):
                os.remove(item_path)

def zip_images(file_paths, output_dir="result/zip"):
    # result/zip 경로에서 ZIP 파일만 청소
    clean_zip_directory(output_dir)

    today = datetime.now().strftime("%Y-%m-%d")
    zip_file_name = f"{today}_images.zip"
    zip_file_path = os.path.join(output_dir, zip_file_name)
    print("압축하기 위한 파일 인풋값:", file_paths)
    # 파일들을 zip으로 압축
    with zipfile.ZipFile(zip_file_path, 'w') as zipf:
        for file_path in file_paths:
            if os.path.exists(file_path):
                arcname = os.path.basename(file_path)  # 압축 파일 안에서의 파일명
                zipf.write(file_path, arcname=arcname)
    return zip_file_path

