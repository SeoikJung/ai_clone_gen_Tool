import gradio as gr
from ui.gallprocess import get_select_gallery,  load_images_from_folder, move_copy_files_only_img
import torch
from PIL import Image, ImageOps
from diffusers import AutoPipelineForInpainting, UNet2DConditionModel
import diffusers
from simple_lama_inpainting import SimpleLama
from PIL import Image
import os
import uuid
from datetime import datetime
import gc

def file_save_path(image, path ="result/faceinp/" ):
    now = datetime.now().strftime("%Y-%m-%d")
    output_dir = f"{path}{now}"
    unique_id = uuid.uuid4()
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"{unique_id}.png")
    image.save(file_path)
    return image , file_path

def predict(dict, prompt="", negative_prompt="", guidance_scale=7.5, steps=20, strength=1.0, scheduler="EulerDiscreteScheduler"):
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    pipe = AutoPipelineForInpainting.from_pretrained("diffusers/stable-diffusion-xl-1.0-inpainting-0.1", torch_dtype=torch.float16, variant="fp16").to(device)
    print("dict 이 뭔데 : " , dict)

    if negative_prompt == "":
        negative_prompt = None
    scheduler_class_name = scheduler.split("-")[0]

    add_kwargs = {}
    if len(scheduler.split("-")) > 1:
        add_kwargs["use_karras"] = True
    if len(scheduler.split("-")) > 2:
        add_kwargs["algorithm_type"] = "sde-dpmsolver++"

    scheduler = getattr(diffusers, scheduler_class_name)
    pipe.scheduler = scheduler.from_pretrained("stabilityai/stable-diffusion-xl-base-1.0", subfolder="scheduler", **add_kwargs)
    # mask = dict["layers"][0]
    # mask.save('mask_image1.png')
    original_size = dict["background"].size
    init_image = dict["background"].convert("RGB").resize((1024, 1024))

    layer = dict["layers"][0].convert("RGBA").resize((1024, 1024))
    mask = Image.new("RGBA", layer.size, "WHITE") 
    mask.paste(layer, (0, 0), layer)
    mask = ImageOps.invert(mask.convert("L"))

    # mask.save('mask_image2.png')
    output = pipe(prompt = prompt, negative_prompt=negative_prompt, image=init_image, mask_image=mask, guidance_scale=guidance_scale, num_inference_steps=int(steps), strength=strength)
    final_image = output.images[0].resize(original_size)

    image , path = file_save_path(final_image, "result/faceinp/")
    # print(torch.cuda.memory_summary(device=torch.device('cuda'), abbreviated=False))
    del pipe
    gc.collect()
    torch.cuda.empty_cache()
    torch.cuda.ipc_collect()

    # print(torch.cuda.memory_summary(device=torch.device('cuda'), abbreviated=False))

    return image, path , path


def lama_predict(dict):
    simple_lama = SimpleLama()

    init_image = dict["background"].convert("RGB")
    layer = dict["layers"][0].convert("RGBA")
    mask = Image.new("RGBA", layer.size, "WHITE")
    mask.paste(layer, (0, 0), layer)
    mask = ImageOps.invert(mask.convert("L"))

    result = simple_lama(init_image, mask)

    image , path = file_save_path(result, "result/faceinp/")

    del simple_lama
    gc.collect()
    torch.cuda.empty_cache()
    torch.cuda.ipc_collect()

    return image, path, path


def inp_tab():
    with gr.Tab("인페인팅"):
        with gr.Row():
            with gr.Column():
                image = gr.ImageMask(type='pil', label='Inpaint')
                with gr.Row(equal_height=True):
                    with gr.Row():
                        prompt = gr.Textbox(value="clean face", placeholder="Your prompt (what you want in place of what is erased)", show_label=False)
                    with gr.Row( equal_height=True):
                        btn = gr.Button("인페인트")
                        lama_btn = gr.Button("ai 지우개")

                with gr.Accordion(label="Advanced Settings", open=False):
                    with gr.Row( equal_height=True):
                        guidance_scale = gr.Number(value=7.5, minimum=1.0, maximum=20.0, step=0.1, label="guidance_scale")
                        steps = gr.Number(value=20, minimum=10, maximum=30, step=1, label="steps")
                        strength = gr.Number(value=0.99, minimum=0.01, maximum=1.0, step=0.01, label="strength")
                        negative_prompt = gr.Textbox(value="beard", label="negative_prompt", placeholder="Your negative prompt", info="what you don't want to see in the image")
                    with gr.Row( equal_height=True):
                        schedulers = ["DEISMultistepScheduler", "HeunDiscreteScheduler", "EulerDiscreteScheduler", "DPMSolverMultistepScheduler", "DPMSolverMultistepScheduler-Karras", "DPMSolverMultistepScheduler-Karras-SDE"]
                        scheduler = gr.Dropdown(label="Schedulers", choices=schedulers, value="EulerDiscreteScheduler")
                with gr.Row(equal_height=True):
                    state_inp_mus_path = gr.State("result/facemustache")
                    state_inp_mus_select_image = gr.State()

                    inp_mus_images = gr.Gallery(label="작업이미지",interactive=False)
                    inp_mus_refresh_btn = gr.Button("새로고침")
                    # inp_mus_images_select_one = gr.Image(interactive=False)

                    inp_mus_refresh_btn.click(fn=load_images_from_folder,inputs=[state_inp_mus_path],outputs=[inp_mus_images])
                    inp_mus_images.select(fn=get_select_gallery, outputs=[image, state_inp_mus_select_image])

                    
            with gr.Column():
                state_output_result_image = gr.State()

                image_out = gr.Image(label="Output", interactive=False)
                inp_output_down = gr.File()
                output_to_input_btn = gr.Button("결과 이미지 다시 사용")
                
                inp_fs_path = gr.State("result/faceswap/")
                inp_fs_one_mv = gr.Button("결과이미지->FS")
                inp_info_txt = gr.Textbox(interactive=False)

                inp_fs_one_mv.click(fn=move_copy_files_only_img, inputs=[state_output_result_image, inp_fs_path],outputs=[inp_info_txt])

                
    lama_btn.click(fn=lama_predict, inputs=[image], outputs=[image_out, inp_output_down, state_output_result_image])
    btn.click(fn=predict, inputs=[image, prompt, negative_prompt, guidance_scale, steps, strength, scheduler], outputs=[image_out, inp_output_down, state_output_result_image ])
    output_to_input_btn.click(fn=lambda x: x, inputs=[image_out],outputs=[image])