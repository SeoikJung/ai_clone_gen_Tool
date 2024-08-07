import gradio as gr
from utils.prompt import generate_base_prompt, generate_sub_prompt
from metadata.translations import TRANSLATIONS, REVERSE_TRANSLATIONS
from ui.dropdown import get_translated_options, get_dropdown_options, toggle_sliders
import os
import json
import metadata.key as meta_key  # key로 RACES와 SEXS 값을 가져옴

def gradio_search(model_select,
                    races, ages, sex, 
                    skin_texture, skin_tone, 
                    hair_color, hair_style, eyes_color, 
                    camera, display, light, adj):

    print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
    selections = {
        "model_path": model_select,
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

        elif category_type == "model_path":
            prompt = model_select
            
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
    print("검색 프롬프트 : ",prompts)

    directory = "result/portrait"
    data = load_json_files(directory)
    index = index_metadata(data)
    # 이미지 검색
    results = search_images(index, prompts)
    print("Found images:", results)


    return results, results


# Step 1: Load all JSON files from the directory recursively
def load_json_files(directory):
    data = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                with open(os.path.join(root, file), 'r') as f:
                    data.append(json.load(f))
    return data

# Step 2: Index Metadata
def index_metadata(data):
    index = []
    for entry in data:
        metadata = {
            "model_path": entry.get("model_path"),
            "file_path": entry.get("file_path"),
            "RACES": entry.get("RACES"),
            "AGES": entry.get("AGES"),
            "SEXS": entry.get("SEXS"),
            "SKIN_TEXTURES": entry.get("SKIN_TEXTURES"),
            "SKIN_TONES": entry.get("SKIN_TONES"),
            "HAIR_COLORS": entry.get("HAIR_COLORS"),
            "HAIR_STYLES": entry.get("HAIR_STYLES"),
            "EYE_COLORS": entry.get("EYE_COLORS"),
            "FILM_TYPES": entry.get("FILM_TYPES"),
            "DISPLAY_TYPES": entry.get("DISPLAY_TYPES"),
            "LIGHTING_TYPES": entry.get("LIGHTING_TYPES"),
            "ADDITIONAL_ADJECTIVES": entry.get("ADDITIONAL_ADJECTIVES")
        }
        index.append(metadata)
    return index

# Step 3: Implement Search Function
def search_images(index, prompts):
    # Example check for RACES and SEXS structure
    print(meta_key.RACES)  # RACES 사전이 올바르게 로드되었는지 확인
    print(meta_key.SEXS)  # SEXS 사전이 올바르게 로드되었는지 확인
    results = []
    for entry in index:
        match = True
        for key, value in prompts.items():
            if value:  # 값이 있을 때만 검사
                if key == "RACES":  # RACES 예외 처리
                    matched_group = None
                    for group, values in meta_key.RACES.items():
                        if value in values:
                            matched_group = group
                            break
                    if matched_group and entry.get(key) not in meta_key.RACES[matched_group]:
                        match = False
                        break
                elif key == "SEXS":  # SEXS 예외 처리
                    matched_group = None
                    for group, values in meta_key.SEXS.items():
                        if value in values:
                            matched_group = group
                            break
                    if matched_group and entry.get(key) not in meta_key.SEXS[matched_group]:
                        match = False
                        break
                else:  # 일반 키 처리
                    if entry.get(key) != value:  # 값이 일치하지 않으면 매치 실패
                        match = False
                        break
        if match:  # 모든 조건이 일치하는 경우
            results.append(entry["file_path"])
    return results


def search_tab():
    options = get_dropdown_options()
    with gr.Tab("검색"):
        with gr.Row():
            shc_image_info_txt = gr.Textbox(label="선택이미지 정보")
        with gr.Row():
            with gr.Column(scale=1, min_width=200):
                sch_model_select = gr.Dropdown(label="모델", choices=["models/RealVisXL_V4.0", 
                                                                    "models/Juggernaut-X-v10", 
                                                                    "models/Juggernaut-XL-v9", "models/XXMix_9realisticSDXL_V1.0_xl_fp16"], value="models/RealVisXL_V4.0")

                sch_races = gr.Dropdown(label="Races", choices=get_translated_options(options["RACES"]), value="선택안함")
                sch_ages = gr.Dropdown(label="Ages", choices=get_translated_options(options["AGES"]), value="선택안함")
                sch_sex = gr.Dropdown(label="Sex", choices=get_translated_options(options["SEXS"]), value="선택안함")

            with gr.Column(scale=1, min_width=200):
                sch_skin_texture = gr.Dropdown(label="Skin Texture", choices=get_translated_options(options["SKIN_TEXTURES"]), value="선택안함")
                sch_skin_tone = gr.Dropdown(label="Skin Tone", choices=get_translated_options(options["SKIN_TONES"]), value="선택안함")
                sch_hair_color = gr.Dropdown(label="Hair Color", choices=get_translated_options(options["HAIR_COLORS"]), value="선택안함")
                sch_hair_style = gr.Dropdown(label="Hair Style", choices=get_translated_options(options["HAIR_STYLES"]), value="선택안함")
                sch_eyes_color = gr.Dropdown(label="Eyes Color", choices=get_translated_options(options["EYE_COLORS"]), value="선택안함")

            with gr.Column(scale=1, min_width=200):
                sch_camera = gr.Dropdown(label="Camera", choices=get_translated_options(options["FILM_TYPES"]), value="선택안함")
                sch_display = gr.Dropdown(label="Display", choices=get_translated_options(options["DISPLAY_TYPES"]), value="선택안함")
                sch_light = gr.Dropdown(label="Light", choices=get_translated_options(options["LIGHTING_TYPES"]), value="선택안함")
                sch_adj = gr.Dropdown(label="Adjectives", choices=get_translated_options(options["ADDITIONAL_ADJECTIVES"]), value="선택안함")

            with gr.Column(scale=3, min_width=200):
                state_sch_output_paths = gr.State()

                search_btn = gr.Button("검색")
                sch_output_images = gr.Gallery(label="결과이미지", interactive=False, columns=[3], rows=[3])
                select_img_one = gr.Image(label="선택이미지", interactive=False)

                search_btn.click(fn=gradio_search, inputs=[sch_model_select, sch_races, sch_ages, sch_sex, 
                                                           sch_skin_texture, sch_skin_tone, sch_hair_color, 
                                                           sch_hair_style, sch_eyes_color, sch_camera, sch_display, 
                                                           sch_light, sch_adj],
                                                    outputs=[sch_output_images, state_sch_output_paths])