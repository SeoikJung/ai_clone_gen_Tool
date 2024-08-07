from metadata.translations import TRANSLATIONS, REVERSE_TRANSLATIONS
import metadata.key as key
import gradio as gr

# 슬라이더 보이기/숨기기 함수
def toggle_sliders(show):
    return gr.update(visible=show), gr.update(visible=show)

# 번역된 선택지 목록을 생성하는 함수
def get_translated_options(options_list):
    translated_options = ["랜덤", "선택안함"] + [TRANSLATIONS[option] for option in options_list]
    return translated_options

# 각 상수 리스트를 가져오는 함수
def get_dropdown_options():
    options = {
        "RACES": list(key.RACES.keys()),
        "AGES": key.AGES,
        "SEXS": list(key.SEXS.keys()),
        "SKIN_TEXTURES": key.SKIN_TEXTURES,
        "SKIN_TONES": key.SKIN_TONES,
        "HAIR_COLORS": key.HAIR_COLORS,
        "HAIR_STYLES": key.HAIR_STYLES,
        "EYE_COLORS": key.EYE_COLORS,
        "FILM_TYPES": key.FILM_TYPES,
        "DISPLAY_TYPES": key.DISPLAY_TYPES,
        "LIGHTING_TYPES": key.LIGHTING_TYPES,
        "ADDITIONAL_ADJECTIVES": key.ADDITIONAL_ADJECTIVES
    }
    return options