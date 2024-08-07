import tyro
import gradio as gr
import os.path as osp
from src.utils.helper import load_description
from src.gradio_pipeline import GradioPipeline
from src.config.crop_config import CropConfig
from src.config.argument_config import ArgumentConfig
from src.config.inference_config import InferenceConfig
import cv2
import torch
import gc
# import gdown
# folder_url = f"https://drive.google.com/drive/folders/1UtKgzKjFAOmZkhNK-OYT0caJ_w2XAnib"
# gdown.download_folder(url=folder_url, output="pretrained_weights", quiet=False)

def partial_fields(target_class, kwargs):
    return target_class(**{k: v for k, v in kwargs.items() if hasattr(target_class, k)})


def initialize_pipeline():
    # set tyro theme
    tyro.extras.set_accent_color("bright_cyan")
    args = tyro.cli(ArgumentConfig)

    # specify configs for inference
    inference_cfg = partial_fields(InferenceConfig, args.__dict__)
    crop_cfg = partial_fields(CropConfig, args.__dict__)

    gradio_pipeline = GradioPipeline(
        inference_cfg=inference_cfg,
        crop_cfg=crop_cfg,
        args=args
    )

    return gradio_pipeline

# # set tyro theme
# tyro.extras.set_accent_color("bright_cyan")
# args = tyro.cli(ArgumentConfig)

# # specify configs for inference
# inference_cfg = partial_fields(InferenceConfig, args.__dict__)  # use attribute of args to initial InferenceConfig
# crop_cfg = partial_fields(CropConfig, args.__dict__)  # use attribute of args to initial CropConfig

# gradio_pipeline = GradioPipeline(
#     inference_cfg=inference_cfg,
#     crop_cfg=crop_cfg,
#     args=args
# )

def gpu_wrapped_execute_video(*args, **kwargs):
    gradio_pipeline = initialize_pipeline()
    
    result = gradio_pipeline.execute_video(*args, **kwargs)
    del gradio_pipeline
    gc.collect()
    torch.cuda.empty_cache()
    torch.cuda.ipc_collect()
    return result


    return gradio_pipeline.execute_video(*args, **kwargs)

def is_square_video(video_path):
    video = cv2.VideoCapture(video_path)

    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

    video.release()
    if width != height:
        raise gr.Error("Error: the video does not have a square aspect ratio. We currently only support square videos")

    return gr.update(visible=True)

def on_button_click(*comp_args):
    return gpu_wrapped_execute_video(*comp_args)

# assets
example_portrait_dir = "assets/examples/source"
example_video_dir = "assets/examples/driving"
data_examples = [
    [osp.join(example_portrait_dir, "s9.jpg"), osp.join(example_video_dir, "d0.mp4"), True, True, True, True],
    [osp.join(example_portrait_dir, "s6.jpg"), osp.join(example_video_dir, "d0.mp4"), True, True, True, True],
    [osp.join(example_portrait_dir, "s10.jpg"), osp.join(example_video_dir, "d0.mp4"), True, True, True, True],
    [osp.join(example_portrait_dir, "s5.jpg"), osp.join(example_video_dir, "d18.mp4"), True, True, True, True],
    [osp.join(example_portrait_dir, "s7.jpg"), osp.join(example_video_dir, "d19.mp4"), True, True, True, True],
    [osp.join(example_portrait_dir, "s22.jpg"), osp.join(example_video_dir, "d0.mp4"), True, True, True, True],
]
#################### interface logic ####################
# Define components first
eye_retargeting_slider = gr.Slider(minimum=0, maximum=0.8, step=0.01, label="target eyes-open ratio",visible=False)
lip_retargeting_slider = gr.Slider(minimum=0, maximum=0.8, step=0.01, label="target lip-open ratio",visible=False)
retargeting_input_image = gr.Image(type="filepath")
output_image = gr.Image(type="numpy")
output_image_paste_back = gr.Image(type="numpy")
output_video = gr.Video()
output_video_concat = gr.Video()


def live_portrait_tab():
    with gr.Tab("live_portrait"):
            with gr.Row():
                with gr.Accordion(open=True, label="Source Portrait"):
                    image_input = gr.Image(type="filepath")
                    gr.Examples(
                        examples=[
                            [osp.join(example_portrait_dir, "s9.jpg")],
                            [osp.join(example_portrait_dir, "s6.jpg")],
                            [osp.join(example_portrait_dir, "s10.jpg")],
                            [osp.join(example_portrait_dir, "s5.jpg")],
                            [osp.join(example_portrait_dir, "s7.jpg")],
                            [osp.join(example_portrait_dir, "s12.jpg")],
                            [osp.join(example_portrait_dir, "s22.jpg")],
                        ],
                        inputs=[image_input],
                        cache_examples=False,
                    )
                with gr.Accordion(open=True, label="Driving Video"):
                    video_input = gr.Video()
                    gr.Examples(
                        examples=[
                            [osp.join(example_video_dir, "d0.mp4")],
                            [osp.join(example_video_dir, "d18.mp4")],
                            [osp.join(example_video_dir, "d19.mp4")],
                            [osp.join(example_video_dir, "d14_trim.mp4")],
                            [osp.join(example_video_dir, "d6_trim.mp4")],
                        ],
                        inputs=[video_input],
                        cache_examples=False,
                    )
            with gr.Row():
                with gr.Accordion(open=False, label="Animation Instructions and Options",visible=False):
                    # gr.Markdown(load_description("assets/gradio_description_animation.md"))
                    with gr.Row():
                        flag_relative_input = gr.Checkbox(value=True, label="relative motion")
                        flag_do_crop_input = gr.Checkbox(value=True, label="do crop")
                        flag_remap_input = gr.Checkbox(value=True, label="paste-back")
            # gr.Markdown(load_description("assets/gradio_description_animate_clear.md"))
            with gr.Row():
                with gr.Column():
                    process_button_animation = gr.Button("🚀 Animate", variant="primary")
                with gr.Column():
                    process_button_reset = gr.ClearButton([image_input, video_input, output_video, output_video_concat], value="🧹 Clear")
            with gr.Row():
                with gr.Column():
                    with gr.Accordion(open=True, label="The animated video in the original image space"):
                        output_video.render()
                with gr.Column():
                    with gr.Accordion(open=True, label="The animated video"):
                        output_video_concat.render()

# ffmpeg -i Ori_C2_2404051651_0005_Dimitri_crop.mp4 -ss 00:01:23 -c copy front_interval_crop.mp4
# ffmpeg -i Ori_C1_2404051651_0005_Dimitri_crop.mp4 -ss 00:01:23 -c copy side_interval_crop.mp4
            process_button_animation.click(
                # fn=gpu_wrapped_execute_video,
                fn=on_button_click,

                inputs=[
                    image_input,
                    video_input,
                    flag_relative_input,
                    flag_do_crop_input,
                    flag_remap_input
                ],
                outputs=[output_video, output_video_concat],
                show_progress=True
            )

            video_input.upload(
                fn=is_square_video,
                inputs=video_input,
                outputs=video_input
            )

