import json
from metadata.translations import TRANSLATIONS
import os
import gradio as gr
from datetime import datetime

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

def get_translated_metadata(metadata):
    keys_to_translate = [
        "RACES", "AGES", "SEXS", "SKIN_TEXTURES", "SKIN_TONES",
        "HAIR_COLORS", "HAIR_STYLES", "EYE_COLORS", "FILM_TYPES",
        "DISPLAY_TYPES", "LIGHTING_TYPES", "ADDITIONAL_ADJECTIVES"
    ]
    translated_values = []
    for key in keys_to_translate:
        if key in metadata and metadata[key] is not None:
            value = metadata[key]
            translated_value = TRANSLATIONS.get(value, value)
            translated_values.append(translated_value)
    return translated_values

def load_and_translate_metadata(evt: gr.SelectData):
    orig_name = evt.value['image']['orig_name']
    today = datetime.now().strftime("%Y-%m-%d")
    new_json_path = os.path.join(f"result/portrait/{today}", orig_name.replace('.png', '.json'))
    
    try:
        with open(new_json_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
            translated_values = get_translated_metadata(metadata)
            result_string = ', '.join(translated_values)
            return result_string
    except FileNotFoundError:
        print(f"Error: {new_json_path} not found")
        return None
    
def load_and_translate_metadata_var(evt: gr.SelectData):
    orig_name = evt.value['image']['orig_name']
    today = datetime.now().strftime("%Y-%m-%d")
    new_json_path = os.path.join(f"result/portrait/{today}", orig_name.replace('.png', '.json'))
    
    try:
        with open(new_json_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
            translated_values = get_translated_metadata(metadata)
            result_string = ', '.join(translated_values)
            values = translated_values
            print(translated_values)
            
            cfg = metadata["cfg"]
            steps = metadata["steps"]
            
            return (
        gr.update(),  # races 값을 변경하지 않음
        gr.update(value=values[1]),  # ages
        gr.update(),  # sex 값을 변경하지 않음
        gr.update(value=values[3]),  # skin_texture
        gr.update(value=values[4]),  # skin_tone
        gr.update(value=values[5]),  # hair_color
        gr.update(value=values[6]),  # hair_style
        gr.update(value=values[7]),  # eyes_color
        gr.update(value=values[8]),  # camera
        gr.update(value=values[9]),  # display
        gr.update(value=values[10]), # light
        gr.update(value=values[11]),  # adj
        gr.update(value=steps),  # steps
        gr.update(value=cfg)  # cfg

    )
            return result_string
        
        
    except FileNotFoundError:
        print(f"Error: {new_json_path} not found")
        return None