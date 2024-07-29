import random
from typing import Optional, Tuple
from metadata.key import RACES, SEXS
import metadata.key as key

def generate_base_prompt(category_type: str, category: str) -> Optional[str]:
    if category_type not in ['RACES', 'SEXS']:
        print("error : RACES, SEXS 값이 존재하지 않습니다.")
        return None
    
    categories = RACES if category_type == 'RACES' else SEXS

    if category == "random":
        category = random.choice(list(categories.keys()))
        return random.choice(categories[category])
    elif category == "no select":
        return ""
    elif category in categories:
        return random.choice(categories[category])
    else:
        return None

def trace_base_prompt(result: str) -> Optional[Tuple[str, str]]:
    for category_type, categories in [('RACES', RACES), ('SEXS', SEXS)]:
        for category, values in categories.items():
            if result in values:
                return (category_type, category)
    return None


def generate_sub_prompt(attribute: str, option: str) -> Optional[str]:
    try:
        options_list = getattr(key, attribute)
    except AttributeError:
        print(f"Error: {attribute} is not a valid attribute")
        return None

    if option == "random":
        return random.choice(options_list)
    elif option == "no select":
        return ""
    elif option in options_list:
        return option
    else:
        return None


def trace_sub_prompt(result: str) -> Optional[Tuple[str, str]]:
    for attribute in dir(key):
        if not attribute.startswith('__'):
            options_list = getattr(key, attribute)
            if result in options_list:
                return (attribute, result)
    return None