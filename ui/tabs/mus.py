import gradio as gr
import metadata.key as key
from metadata.translations import TRANSLATIONS, REVERSE_TRANSLATIONS
from utils.prompt import generate_base_prompt, generate_sub_prompt
from utils.portrait import PortraitGenerator 
from utils.zippath import zip_images
from metadata.metadata import load_and_translate_metadata
from ui.gallprocess import get_select_gallery, move_copy_files , load_images_from_folder
import random
import torch
import gc
import json


def gradio_mus_generator(paths):
    image_path, json_path = paths
    images = []
    file_paths = []
    mus = ["mustache", "beard", "stubble", "sideburns" , "goatee", "facial hair"]
    
    with open(json_path, "r", encoding="utf-8") as f:
        config = json.load(f)
        model_path = config["model_path"]

    for m in mus:
        
        negative_prompt = f"{m}, bad eyes, cgi, airbrushed, plastic, watermark"

        generator = PortraitGenerator(model_path)
        generator.load_settings(json_path)
        generator.set_settings(
            negative_prompt=negative_prompt,
        )
        image , file_path = generator.generate()
        torch.cuda.empty_cache()
        images.append(image)
        file_paths.append(file_path)


    generator.wipe_memory()
    del generator
    gc.collect()
    torch.cuda.empty_cache()
    torch.cuda.ipc_collect()

    images_path = file_paths.copy()
    zip_path = zip_images(file_paths)
    file_paths.append(zip_path)
    return images_path, images_path, file_paths


def mus_tab():

    with gr.Tab("수염제거"):
        with gr.Row():
            with gr.Column(scale=1 , min_width=200):
                state_mus_path = gr.State("result/facemustache")
                state_mus_select_image = gr.State()

                mus_images = gr.Gallery(label="작업이미지", interactive=False)
                mus_refresh_btn = gr.Button("새로고침")
                mus_images_select_one = gr.Image(label="선택이미지",interactive=False)

                mus_refresh_btn.click(fn=load_images_from_folder,inputs=[state_mus_path],outputs=[mus_images])
                mus_images.select(fn=get_select_gallery, outputs=[mus_images_select_one, state_mus_select_image])

            with gr.Column(scale=2, min_width=200):
                state_output_images_path = gr.State()
                mus_output_images = gr.Gallery(label="결과이미지",interactive=False)
                mus_output_images_down = gr.File(label="다운로드",)

                mus_rm_btn = gr.Button("수염 제거")
                mus_rm_btn.click(fn=gradio_mus_generator,
                                 inputs=[state_mus_select_image],
                                 outputs=[mus_output_images, state_output_images_path, mus_output_images_down])


            with gr.Column(scale=1 , min_width=200):
                state_output_select_image = gr.State()

                mus_fs_path = gr.State("result/faceswap/")
                mus_mus_path = gr.State("result/facemustache")
                mus_var_path = gr.State("result/facevar")

                mus_fs_one_mv = gr.Button("선택이미지->FS")
                mus_mus_one_mv = gr.Button("선택이미지->MUS")
                mus_var_one_mv = gr.Button("선택이미지->VAR")
                mus_info_txt = gr.Textbox(label="이동확인메세지",interactive=False)

                mus_output_select_one = gr.Image(interactive=False)
                mus_output_images.select(fn=get_select_gallery, outputs=[mus_output_select_one, state_output_select_image])
                
                mus_fs_one_mv.click(fn=move_copy_files, inputs=[state_output_select_image, mus_fs_path],outputs=[mus_info_txt])
                mus_mus_one_mv.click(fn=move_copy_files, inputs=[state_output_select_image, mus_mus_path],outputs=[mus_info_txt])
                mus_var_one_mv.click(fn=move_copy_files, inputs=[state_output_select_image, mus_var_path],outputs=[mus_info_txt])


