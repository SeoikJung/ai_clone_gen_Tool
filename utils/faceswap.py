import os
from PIL import Image
import subprocess
from ui.gallprocess import clear_directory, img_list
import shutil
from datetime import datetime
from utils.restore import inference
from utils.zippath import zip_images

def copy_images_to_directory():
    today_date = datetime.now().strftime("%Y-%m-%d")
    source_directory = f'result/faceswap/{today_date}/'
    destination_directory = f'result/roop/source_tmp/{today_date}/'
    
    # 디렉토리가 없으면 생성
    if not os.path.exists(destination_directory):
        os.makedirs(destination_directory)
    
    # 파일 확장자 설정
    valid_extensions = ('.png', '.jpg', '.jpeg')
    
    for filename in os.listdir(source_directory):
        if filename.lower().endswith(valid_extensions):
            source_path = os.path.join(source_directory, filename)
            destination_path = os.path.join(destination_directory, filename)
            shutil.copy2(source_path, destination_path)
            print(f'Copied {source_path} to {destination_path}')


def roopGAN(source_images, base_image , gfp_scale, gfp_version):
    print("소스이미지 출력 : ", source_images)
    ### 시작할때 폴더 청소
    today_date = datetime.now().strftime("%Y-%m-%d")
    directory = f'result/roop/source_tmp/{today_date}/'
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    clear_directory(directory)

    # source_images 리스트에서 파일 경로 추출 및 복사
    for image_info in source_images:
        source_path = image_info[0]
        if source_path and os.path.isfile(source_path):
            filename = os.path.basename(source_path)
            destination_path = os.path.join(directory, filename)
            shutil.copy2(source_path, destination_path)
            print(f'Copied {source_path} to {destination_path}')
        else:
            print(f'Skipping invalid path: {source_path}')

    # copy_images_to_directory()
    #####################

    # 디렉토리 경로
    target_image_path = "result/roop/target_tmp/target.png"
    if not os.path.exists("result/roop/target_tmp"):
        os.makedirs("result/roop/target_tmp")
    base_image = Image.fromarray(base_image)
    base_image.save(target_image_path)

    directory = f"result/roop/result/{today_date}"
    clear_directory(directory)

    script_path = "lib/roop/batch2.py"
    command = ["python", script_path]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("Error:", e.stderr)
    

    images , paths = img_list(directory)
    imgs = []
    pths = []
    for img in paths:
        img, pth = inference(img, version=gfp_version, scale=gfp_scale)
        imgs.append(img)
        pths.append(pth)
    zips = zip_images(pths, output_dir=f"result/zip")
    pths_zip = pths.copy()
    pths_zip.append(zips)
    return pths, pths_zip



    source_directory = f'result/roop/source_tmp/{today_date}/'  # 소스 이미지 폴더
    target_image_path = "result/roop/target_tmp/target.png"  # 타겟 이미지
    output_directory = f'result/roop/result/{today_date}'  # 결과 저장 폴더

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)