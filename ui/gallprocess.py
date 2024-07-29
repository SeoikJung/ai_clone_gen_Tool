import os
import gradio as gr
from datetime import datetime
import shutil
from PIL import Image

def img_list(path):
    # folder = path
    images = []
    images_paths = []
    # os.listdir()로 폴더 내 파일 목록을 가져오고, 파일 이름에 숫자 부분을 기준으로 정렬
    # files = sorted(os.listdir(path), key=lambda x: int(x.split('.')[0]))
    files = os.listdir(path)
    for filename in files:
        if filename.endswith(".png") or filename.endswith(".jpg"):
            img_path = os.path.join(path, filename)
            img = Image.open(img_path)

            images_paths.append(img_path)
            images.append(img)
    return images ,images_paths

def load_images_from_folder(path):
    today = datetime.now().strftime("%Y-%m-%d")
    dir = os.path.join(path, today)
    os.makedirs(dir, exist_ok=True)

    images ,paths = img_list(dir)
    return paths

def clear_directory(directory):
    # 디렉토리가 존재하는지 확인
    if os.path.exists(directory):
        # 디렉토리 내의 모든 파일 및 하위 디렉토리 삭제
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            try:
                # 파일이면 삭제
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                # 디렉토리면 디렉토리 삭제
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')

def get_select_gallery(evt: gr.SelectData):

    image_path = evt.value['image']['path']  # 이미지 경로를 가져옴
    orig_name = evt.value['image']['orig_name']  # 원래 이름을 가져옴
    
    # print(f"==>> evt.selected: {evt.selected}") # True
    # print(f"==>> evt._data: {evt._data}") # {'index': 1, 'value': None}
    # print(f"You selected {evt.value} at {evt.index} from {evt.target}") # You selected None at 1 from gallery
    print(f"Image path: {image_path}")  # 이미지 경로 출력
    print(f"Original name: {orig_name}")  # 원래 이름 출력
    
    today = datetime.now().strftime("%Y-%m-%d")
    new_imgae_path = os.path.join(f"result/portrait/{today}", orig_name)
    new_json_path = os.path.join(f"result/portrait/{today}", orig_name.replace('.png', '.json'))
    new_path = (new_imgae_path, new_json_path)
    print(f"New path: {new_path}")  

    return image_path, new_path


def move_copy_files(state_select_image, destination_path):
    # state_select_image에서 이미지와 JSON 파일 경로를 가져옴
    image_path, json_path = state_select_image
    today = datetime.now().strftime("%Y-%m-%d")

    # 복사할 파일 경로 설정
    image_dest_path = os.path.join(destination_path, today, os.path.basename(image_path))
    json_dest_path = os.path.join(destination_path, today, os.path.basename(json_path))

    # 디렉토리가 없는 경우 생성
    if not os.path.exists(os.path.dirname(image_dest_path)):
        os.makedirs(os.path.dirname(image_dest_path))

    # 파일 복사
    shutil.copy2(image_path, image_dest_path)
    shutil.copy2(json_path, json_dest_path)

    return f"이동 완료되었습니다. {image_path},{destination_path}"


def move_copy_files_only_img(state_select_image, destination_path):
    # state_select_image에서 이미지와 JSON 파일 경로를 가져옴
    image_path = state_select_image
    today = datetime.now().strftime("%Y-%m-%d")

    # 복사할 파일 경로 설정
    image_dest_path = os.path.join(destination_path, today, os.path.basename(image_path))

    # 디렉토리가 없는 경우 생성
    if not os.path.exists(os.path.dirname(image_dest_path)):
        os.makedirs(os.path.dirname(image_dest_path))

    # 파일 복사
    shutil.copy2(image_path, image_dest_path)

    return f"이동 완료되었습니다. {image_path},{destination_path}"

