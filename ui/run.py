import gradio as gr
import time
from ui.tabs.gen import gen_tab
from ui.tabs.fs import fs_tab
from ui.tabs.mus import mus_tab
from ui.tabs.inp import inp_tab
from ui.tabs.restor import restor_tab
from ui.tabs.var import var_tab
from ui.tabs.set import setting_tab 
from ui.tabs.search import search_tab 
from ui.tabs.liveport import live_portrait_tab
from ui.tabs.video_edit import video_edit_tab
import ui.globals as uii
import torch
import os
import sys


def run():
    with gr.Blocks(analytics_enabled=False) as demo:
        gen_tab()
        mus_tab()
        inp_tab()
        restor_tab()
        fs_tab()
        var_tab()
        search_tab ()
        live_portrait_tab()
        video_edit_tab()
        setting_tab(demo)
    torch.cuda.empty_cache()  
    demo.queue(default_concurrency_limit=1).launch(server_port=8888, server_name='0.0.0.0')


