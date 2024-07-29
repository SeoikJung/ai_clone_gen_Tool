import gradio as gr
from ui.tabs.gen import gen_tab
from ui.tabs.fs import fs_tab
from ui.tabs.mus import mus_tab
from ui.tabs.inp import inp_tab
from ui.tabs.restor import restor_tab
from ui.tabs.var import var_tab

import torch


def run():
    with gr.Blocks() as demo:
        gen_tab()
        mus_tab()
        inp_tab()
        restor_tab()
        fs_tab()
        var_tab()
        # 가정: model이 이미 생성되어 있고 GPU에 로드되어 있음
    torch.cuda.empty_cache()  # GPU 캐시 메모리 정리

    demo.launch(server_port=8888, server_name='0.0.0.0')