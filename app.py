from ui.interface import GradioInterface

if __name__ == "__main__":
    data_path = 'metadata/prompt/data.json'
    trans_key_path = 'metadata/prompt/trans_key.json'
    trans_value_path = 'metadata/prompt/trans_value.json'
    
    interface = GradioInterface(data_path, trans_key_path, trans_value_path)
    interface.launch_interface()
