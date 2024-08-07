
import gradio as gr
from ui.gallprocess import clear_directory
import ui.globals as uii
import os
import sys
import subprocess

def restart():

    print("서버 재시작 중...")
    gr.Error("서버 재시작 중...")
    uii.ui_restart_server = True

    python = sys.executable
    os.execl(python, python, *sys.argv)
    # os.execv(sys.executable, ['python'] + sys.argv)


def setting_tab(demo):
    with gr.Tab("캐시삭제"):
        with gr.Row():
            with gr.Column():
                setting_btn = gr.Button("캐시삭제")
                button_apply_restart = gr.Button("서버 재시작")

                state_setting = gr.State("/tmp/gradio")
                rm_cache_txt = gr.Textbox(interactive=False)
                setting_btn.click(fn=clear_directory ,inputs=[state_setting], outputs=[rm_cache_txt])
                button_apply_restart.click(fn=restart)