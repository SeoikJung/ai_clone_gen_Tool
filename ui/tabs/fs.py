import gradio as gr
from ui.gallprocess import  load_images_from_folder
from utils.faceswap import roopGAN
import os
from datetime import datetime
import shutil

def move_copy_files(state_select_image, destination_path):
    # state_select_image에서 이미지와 JSON 파일 경로를 가져옴
    image_path, json_path = state_select_image
    today = datetime.now().strftime("%Y-%m-%d")

    image_dest_path = os.path.join(destination_path, today, os.path.basename(image_path))
    json_dest_path = os.path.join(destination_path, today, os.path.basename(json_path))

    if not os.path.exists(os.path.dirname(image_dest_path)):
        os.makedirs(os.path.dirname(image_dest_path))

    shutil.copy2(image_path, image_dest_path)
    shutil.copy2(json_path, json_dest_path)

    return f"이동 완료되었습니다. {image_path},{destination_path}"

def test(gallery , destination_path):
    print(gallery)
    today = datetime.now().strftime("%Y-%m-%d")
    gen_folder = os.path.join(destination_path,today)

    os.makedirs(gen_folder , exist_ok=True)
    for gall in gallery:
        image_path , _ = gall
        image_dest_path = os.path.join(destination_path, today, os.path.basename(image_path))

        shutil.copy2(image_path, image_dest_path)


    return f"이동 완료되었습니다. {image_path},{destination_path}"

def fs_tab():
    with gr.Tab("FaceSwap"):
            with gr.Row():
                with gr.Column(scale=2):
                    state_fs_path = gr.State("result/faceswap")
                    fs_images = gr.Gallery(label = "Source 이미지", columns=[3], rows=[3],interactive=True)
                    fs_refresh_btn = gr.Button("새로고침")
                    fs_refresh_btn.click(fn=load_images_from_folder,inputs=[state_fs_path],outputs=[fs_images])

                    fs_select = gr.Radio(['v1.2', 'v1.3', 'v1.4', 'RestoreFormer'], type="value", value='v1.4', label='version')
                    fs_num = gr.Slider(1, 3, step = 0.1, label="Rescaling factor", value=2, info="1~3")
                    # fs_num = gr.Number(label="Rescaling factor", value=2)


                with gr.Column(scale=1):
                    img_upload = gr.Image(label = "Target 이미지")
                    fs_bt = gr.Button("다중 페이스 스왑")
                    fs_down = gr.File(label="다운로드", height=800)

                with gr.Column(scale=2):
                    state_cluster_path = gr.State("result/facecluster")
                    fs_output = gr.Gallery(label="결과이미지", columns=[3], rows=[3])
                    cl_bt = gr.Button("클러스터링 폴더전송")


            fs_bt.click(fn = roopGAN, inputs = [fs_images, img_upload , fs_num, fs_select], outputs = [fs_output, fs_down])
            cl_bt.click(fn=test, inputs=[fs_output, state_cluster_path])