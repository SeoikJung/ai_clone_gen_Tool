import gradio as gr
import metadata.key as key
from metadata.translations import TRANSLATIONS, REVERSE_TRANSLATIONS
from utils.prompt import generate_base_prompt, generate_sub_prompt
from utils.portrait import PortraitGenerator 
from utils.zippath import zip_images
from metadata.metadata import load_and_translate_metadata, load_and_translate_metadata_var
from ui.gallprocess import get_select_gallery, move_copy_files , load_images_from_folder
from ui.dropdown import get_translated_options, get_dropdown_options, toggle_sliders

import torch
import json
import gc


def gradio_var_generator(paths,races, ages, sex, skin_texture, 
                         skin_tone, hair_color, hair_style, eyes_color, 
                         camera, display, light, adj, steps, cfgs , detail_check,
                         freeu_start, b1, b2, s1, s2):
    image_path, json_path = paths
    images = []
    file_paths = []
    
    with open(json_path, "r", encoding="utf-8") as f:
        config = json.load(f)
        model_path = config["model_path"]
    if model_path == "models/XXMix_9realisticSDXL_V1.0_xl_fp16":
        key_word_emb = "xxmixgirl, "
    else:
        key_word_emb = ""

    prompt = ""
    generator = PortraitGenerator(model_path)
    generator.load_settings(json_path)

    print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
    selections = {
        "AGES": ages,
        "SKIN_TEXTURES": skin_texture,
        "SKIN_TONES": skin_tone,
        "HAIR_COLORS": hair_color,
        "HAIR_STYLES": hair_style,
        "EYE_COLORS": eyes_color,
        "FILM_TYPES": camera,
        "DISPLAY_TYPES": display,
        "LIGHTING_TYPES": light,
        "ADDITIONAL_ADJECTIVES": adj
    }
    prompts ={}
    for category_type, selection in selections.items():
        if category_type in ['RACES', 'SEXS']:
            if selection == "랜덤":
                prompt = generate_base_prompt(category_type, "random")
            elif selection == "선택안함":
                prompt = generate_base_prompt(category_type, "no select")
            else:
                english_value = REVERSE_TRANSLATIONS[selection]
                prompt = generate_base_prompt(category_type, english_value)
        else:
            if selection == "랜덤":
                prompt = generate_sub_prompt(category_type, "random")
            elif selection == "선택안함":
                prompt = generate_sub_prompt(category_type, "no select")
            else:
                english_value = REVERSE_TRANSLATIONS[selection]
                prompt = generate_sub_prompt(category_type, english_value)
        prompts[category_type] = prompt
        print(f"Category Type: {category_type}, Selection: {selection}, Prompt: {prompt}")
    print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
    print(prompts)
    print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
    prompt = f"{key_word_emb}{generator.settings.get('RACES')} {generator.settings.get('SEXS')}, {prompts['AGES']}, (hyperdetailed photography), soft light, head and shoulders portrait, cover, {prompts['SKIN_TONES']}, {prompts['SKIN_TEXTURES']}, {prompts['HAIR_COLORS']}, {prompts['HAIR_STYLES']}, {prompts['EYE_COLORS']}, {prompts['FILM_TYPES']}, {prompts['DISPLAY_TYPES']}, {prompts['LIGHTING_TYPES']}, {prompts['ADDITIONAL_ADJECTIVES']}"
    print(prompt)
    print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")

    print("seed값 유지 : ",generator.settings.get('seed'))
    if detail_check:
        generator.set_settings(
            prompt=prompt,
            cfg = cfgs,
            steps = steps
        )
    else:
        generator.set_settings(
            prompt=prompt
        )
    # 이미지 생성 및 저장
    if freeu_start:
        generator.enable_freeu(s1=s1, s2=s2, b1=b1, b2=b2)
    
    image , file_path = generator.generate()
    print("seed값 유지 : ", generator.settings.get('seed'))

    torch.cuda.empty_cache()
    images.append(image)
    file_paths.append(file_path)

    json_file_path = file_path.replace('.png', '.json')
    # JSON 파일 업데이트
    with open(json_file_path, 'r+', encoding='utf-8') as json_file:
        data = json.load(json_file)
        data.update(prompts)
        json_file.seek(0)
        json.dump(data, json_file, ensure_ascii=False, indent=4)
        json_file.truncate()


    generator.wipe_memory()
    del generator
    gc.collect()
    torch.cuda.empty_cache()
    torch.cuda.ipc_collect()

    images_path = file_paths.copy()
    zip_path = zip_images(file_paths)
    file_paths.append(zip_path)
    return images_path, images_path, file_paths


def var_tab():
    options = get_dropdown_options()

    with gr.Tab("얼굴변형"):
        with gr.Row():
            with gr.Column(scale=1 , min_width=200):
                state_var_path = gr.State("result/facevar")
                state_var_select_image = gr.State()

                var_images = gr.Gallery(label="작업이미지",interactive=False)
                var_refresh_btn = gr.Button("새로고침")
                var_images_select_one = gr.Image(label="선택이미지",interactive=False)
                var_refresh_btn.click(fn=load_images_from_folder,inputs=[state_var_path],outputs=[var_images])

                races_var = gr.Dropdown(label="Races", visible=False, choices=get_translated_options(options["RACES"]), value="랜덤")
                sex_var = gr.Dropdown(label="Sex", visible=False, choices=get_translated_options(options["SEXS"]), value="랜덤")

            with gr.Column(scale=1, min_width=200):
                ages_var = gr.Dropdown(label="Ages", choices=get_translated_options(options["AGES"]), value="랜덤")
                skin_texture_var = gr.Dropdown(label="Skin Texture", choices=get_translated_options(options["SKIN_TEXTURES"]), value="랜덤")
                skin_tone_var = gr.Dropdown(label="Skin Tone", choices=get_translated_options(options["SKIN_TONES"]), value="랜덤")
                hair_color_var = gr.Dropdown(label="Hair Color", choices=get_translated_options(options["HAIR_COLORS"]), value="랜덤")
                hair_style_var = gr.Dropdown(label="Hair Style", choices=get_translated_options(options["HAIR_STYLES"]), value="랜덤")
                eyes_color_var = gr.Dropdown(label="Eyes Color", choices=get_translated_options(options["EYE_COLORS"]), value="랜덤")

            with gr.Column(scale=1, min_width=200):
                camera_var = gr.Dropdown(label="Camera", choices=get_translated_options(options["FILM_TYPES"]), value="랜덤")
                display_var = gr.Dropdown(label="Display", choices=get_translated_options(options["DISPLAY_TYPES"]), value="랜덤")
                light_var = gr.Dropdown(label="Light", choices=get_translated_options(options["LIGHTING_TYPES"]), value="랜덤")
                adj_var = gr.Dropdown(label="Adjectives", choices=get_translated_options(options["ADDITIONAL_ADJECTIVES"]), value="랜덤")

                detail_change = gr.Checkbox(label="구도 변경")
                steps_var = gr.Slider(1, 100, step=1.0, value=40, label="디테일 추가", info="1~100", visible=False)
                cfgs_var = gr.Slider(1, 20, step=1.0, value=6, label="스타일 제어력", info="1~20", visible=False)
                detail_change.change(toggle_sliders, inputs=[detail_change], outputs=[steps_var, cfgs_var])

                freeu_change = gr.Checkbox(label="freeu 사용")
                b1_var = gr.Slider(1, 2, step=0.1, value=1.3, label="b1", info="1~2", visible=False)
                b2_var = gr.Slider(1, 2, step=0.1, value=1.4, label="b2", info="1~2", visible=False)
                s1_var = gr.Slider(1, 2, step=0.1, value=0.9, label="s1", info="1~2", visible=False)
                s2_var = gr.Slider(1, 2, step=0.1, value=0.2, label="s2", info="1~2", visible=False)
                # Stable Diffusion v1.4
                # b1: 1.3, b2: 1.4, s1: 0.9, s2: 0.2
                # Stable Diffusion v1.5
                # b1: 1.5, b2: 1.6, s1: 0.9, s2: 0.2
                # Stable Diffusion v2.1
                # b1: 1.4, b2: 1.6, s1: 0.9, s2: 0.2
                # SDXL
                # b1: 1.3, b2: 1.4, s1: 0.9, s2: 0.2 
                freeu_change.change(toggle_sliders, inputs=[freeu_change], outputs=[b1_var,b2_var])
                freeu_change.change(toggle_sliders, inputs=[freeu_change], outputs=[s1_var,s2_var])



                var_images.select(fn=get_select_gallery, outputs=[var_images_select_one, state_var_select_image])
                var_images.select(fn=load_and_translate_metadata_var, outputs=[
                    races_var, ages_var, sex_var, skin_texture_var, skin_tone_var, hair_color_var, hair_style_var, eyes_color_var,
                    camera_var, display_var, light_var, adj_var,
                    steps_var, cfgs_var

                ])


            with gr.Column(scale=2 , min_width=200):
                var_output_images = gr.Gallery(label="결과이미지",interactive=False)
                var_gen_btn = gr.Button("인종  생성")
                var_select_output_img = gr.Image(label="선택이미지",interactive=False)

            with gr.Column(scale=1 , min_width=200):
                state_var_gallery_all_image = gr.State()
                state_var_output_select_image = gr.State()

                var_fs_path = gr.State("result/faceswap/")
                var_mus_path = gr.State("result/facemustache")
                var_var_path = gr.State("result/facevar")

                var_fs_one_mv = gr.Button("선택이미지->FS")
                var_mus_one_mv = gr.Button("선택이미지->MUS")
                var_var_one_mv = gr.Button("선택이미지->VAR")

                var_info_txt = gr.Textbox(label="이동확인메세지")
                var_output_images_down = gr.File(label="Download")
                var_gen_btn.click(gradio_var_generator, 
                    inputs=[ state_var_select_image,
                            races_var, ages_var, sex_var, 
                            skin_texture_var, skin_tone_var, 
                            hair_color_var, hair_style_var, eyes_color_var, 
                            camera_var, display_var, light_var, adj_var
                            ,steps_var, cfgs_var, detail_change
                            ,freeu_change, b1_var, b2_var, s1_var, s2_var

                            ], 
                    outputs=[var_output_images, state_var_gallery_all_image, var_output_images_down])


                var_fs_one_mv.click(fn=move_copy_files, inputs=[state_var_output_select_image, var_fs_path],outputs=[var_info_txt])
                var_mus_one_mv.click(fn=move_copy_files, inputs=[state_var_output_select_image, var_mus_path],outputs=[var_info_txt])
                var_var_one_mv.click(fn=move_copy_files, inputs=[state_var_output_select_image, var_var_path],outputs=[var_info_txt])

                var_output_images.select(fn=get_select_gallery, outputs=[var_select_output_img,state_var_output_select_image ])

                


