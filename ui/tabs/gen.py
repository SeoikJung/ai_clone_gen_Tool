import gradio as gr
import metadata.key as key
from metadata.translations import TRANSLATIONS, REVERSE_TRANSLATIONS
from utils.prompt import generate_base_prompt, generate_sub_prompt
from utils.portrait import PortraitGenerator 
from utils.zippath import zip_images
from metadata.metadata import load_and_translate_metadata
from ui.gallprocess import get_select_gallery, move_copy_files, move_copy_files_all_img
from ui.dropdown import get_translated_options, get_dropdown_options, toggle_sliders
import random
import torch
import json
import gc


def gradio_portrait_generator(model_select, cnt_img, steps, cfgs, 
                              races, ages, sex, 
                              skin_texture, skin_tone, 
                              hair_color, hair_style, eyes_color, 
                              camera, display, light, adj, detail_check):
    if not detail_check:
        steps = random.randint(1, 100)
        cfgs = random.randint(1, 20)

    if model_select == "models/XXMix_9realisticSDXL_V1.0_xl_fp16":
        key_word_emb = "xxmixgirl, "
    else:
        key_word_emb = ""

    images = []
    file_paths = []
    for _ in range(cnt_img):
        print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
        selections = {
            "RACES": races,
            "AGES": ages,
            "SEXS": sex,
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
        print("prompt dict : ",prompts)
        print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
        prompt = f"{key_word_emb}{prompts['RACES']} {prompts['SEXS']}, {prompts['AGES']}, (hyperdetailed photography), soft light, head and shoulders portrait, cover, {prompts['SKIN_TONES']}, {prompts['SKIN_TEXTURES']}, {prompts['HAIR_COLORS']}, {prompts['HAIR_STYLES']}, {prompts['EYE_COLORS']}, {prompts['FILM_TYPES']}, {prompts['DISPLAY_TYPES']}, {prompts['LIGHTING_TYPES']}, {prompts['ADDITIONAL_ADJECTIVES']}"
        print("prompt : ",prompt)
        print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")

        if model_select == "models/XXMix_9realisticSDXL_V1.0_xl_fp16":
            negative_prompt = "bad eyes, (worst quality, low quality, illustration, 3d, 2d, painting, cartoons, sketch), tooth, open mouth"
        else:
            negative_prompt = f"bad eyes, cgi, airbrushed, plastic, watermark"

        print("nagative_prompt : ", negative_prompt)
        seed = random.randint(0, 2**32 - 1)
        width = 832
        height = 1216
        strength = 0.35
        
        generator = PortraitGenerator(model_select)
        generator.set_settings(
            prompt=prompt,
            seed=seed,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            cfg=cfgs,
            steps=steps,
            strength=strength
        )
        # generator.print_cuda_memory_usage("before image generation")
        # 이미지 생성 및 저장
        image , file_path = generator.generate()
        # generator.print_cuda_memory_usage("after image generation")
        # 인스턴스 삭제 및 GPU 메모리 정리
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
    
    # print(torch.cuda.memory_summary(device=torch.device('cuda'), abbreviated=False))
    # generator.print_cuda_memory_usage("before wiping memory")
    generator.wipe_memory()
    # generator.print_cuda_memory_usage("after wiping memory")
    del generator
    gc.collect()
    torch.cuda.empty_cache()
    torch.cuda.ipc_collect()
    # print(torch.cuda.memory_summary(device=torch.device('cuda'), abbreviated=False))

    images_path = file_paths.copy()
    zip_path = zip_images(file_paths)
    file_paths.append(zip_path)
    return images_path, images_path, file_paths


def gen_tab():
    options = get_dropdown_options()

    with gr.Tab("인물 생성"):
        with gr.Row():
            image_info_txt = gr.Textbox(label="선택이미지 정보")
        with gr.Row():
            with gr.Column(scale=1 , min_width=200):
                model_select = gr.Dropdown(label="모델선정", choices=["models/RealVisXL_V4.0","models/Juggernaut-X-v10","models/Juggernaut-XL-v9", "models/XXMix_9realisticSDXL_V1.0_xl_fp16"],value="models/RealVisXL_V4.0")
                cnt_img = gr.Slider(1, 100, step = 1.0, value=1, label="한 번에 생성", info="1~100")
                
                detail_check = gr.Checkbox(label="구도 고정")
                steps = gr.Slider(1, 100, step = 1.0, value=40, label="디테일 추가", info="1~100", visible=False)
                cfgs = gr.Slider(1, 20, step = 1.0, value=6, label="스타일 제어력", info="1~20", visible=False)
                detail_check.change(toggle_sliders, inputs=[detail_check], outputs=[steps, cfgs])

                races = gr.Dropdown(label="Races", choices=get_translated_options(options["RACES"]), value="랜덤")
                ages = gr.Dropdown(label="Ages", choices=get_translated_options(options["AGES"]), value="랜덤")
                sex = gr.Dropdown(label="Sex", choices=get_translated_options(options["SEXS"]), value="랜덤")

            with gr.Column(scale=1, min_width=200):
                skin_texture = gr.Dropdown(label="Skin Texture", choices=get_translated_options(options["SKIN_TEXTURES"]), value="랜덤")
                skin_tone = gr.Dropdown(label="Skin Tone", choices=get_translated_options(options["SKIN_TONES"]), value="랜덤")
                hair_color = gr.Dropdown(label="Hair Color", choices=get_translated_options(options["HAIR_COLORS"]), value="랜덤")
                hair_style = gr.Dropdown(label="Hair Style", choices=get_translated_options(options["HAIR_STYLES"]), value="랜덤")
                eyes_color = gr.Dropdown(label="Eyes Color", choices=get_translated_options(options["EYE_COLORS"]), value="랜덤")

            with gr.Column(scale=1, min_width=200):
                camera = gr.Dropdown(label="Camera", choices=get_translated_options(options["FILM_TYPES"]), value="랜덤")
                display = gr.Dropdown(label="Display", choices=get_translated_options(options["DISPLAY_TYPES"]), value="랜덤")
                light = gr.Dropdown(label="Light", choices=get_translated_options(options["LIGHTING_TYPES"]), value="랜덤")
                adj = gr.Dropdown(label="Adjectives", choices=get_translated_options(options["ADDITIONAL_ADJECTIVES"]), value="랜덤")

            with gr.Column(scale=2 , min_width=200):
                output_images = gr.Gallery(label="결과이미지", interactive=False)
                gen_btn = gr.Button("인종  생성")
                select_img_one = gr.Image(label="선택이미지",interactive=False)


            with gr.Column(scale=1 , min_width=200):
                state_select_image = gr.State()
                state_gallery_all_image = gr.State()

                fs_path = gr.State("result/faceswap/")
                mus_path = gr.State("result/facemustache")
                var_path = gr.State("result/facevar")

                fs_one_mv = gr.Button("선택이미지->FS")
                fs_many_mv = gr.Button("전체이미지->FS")
                mus_one_mv = gr.Button("선택이미지->MUS")
                var_one_mv = gr.Button("선택이미지->VAR")
                info_txt = gr.Textbox(label="이동확인메세지",interactive=False)
                output_images_down = gr.File(label="Download", height=800)
                gen_btn.click(gradio_portrait_generator, 
                        inputs=[model_select, cnt_img, steps, cfgs, 
                                races, ages, sex, 
                                skin_texture, skin_tone, 
                                hair_color, hair_style, eyes_color, 
                                camera, display, light, adj, detail_check], 
                        outputs=[output_images, state_gallery_all_image, output_images_down])


                fs_one_mv.click(fn=move_copy_files, inputs=[state_select_image, fs_path],outputs=[info_txt])
                fs_many_mv.click(fn=move_copy_files_all_img, inputs=[state_gallery_all_image, fs_path],outputs=[info_txt])
                mus_one_mv.click(fn=move_copy_files, inputs=[state_select_image, mus_path],outputs=[info_txt])
                var_one_mv.click(fn=move_copy_files, inputs=[state_select_image, var_path],outputs=[info_txt])

            
            output_images.select(fn=get_select_gallery, outputs=[select_img_one, state_select_image])
            output_images.select(fn=load_and_translate_metadata, outputs=[image_info_txt])
