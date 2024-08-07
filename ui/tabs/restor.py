
import gradio as gr
from utils.restore import inference

def restor_tab():
    with gr.Tab("저화질복원"):
        with gr.Row():
            with gr.Column():
                restor_image = gr.Image(type="filepath", label="Input")
                restor_select = gr.Radio(['v1.2', 'v1.3', 'v1.4', 'RestoreFormer'], type="value", value='v1.4', label='version')
                restor_num = gr.Number(label="Rescaling factor", value=2)

            with gr.Column():
                restor_output = gr.Image(type="numpy", label="Output")
                restor_down = gr.File(label="Download")
                restor_start = gr.Button("화질복원")
                restor_start.click(fn=inference,inputs=[restor_image, restor_select, restor_num], outputs=[restor_output, restor_down])

# 1.4    2, 1.5