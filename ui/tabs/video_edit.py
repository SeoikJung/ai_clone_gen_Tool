import gradio as gr
import cv2
import numpy as np
from PIL import Image
from autocrop import Cropper
from typing import Optional
import ffmpeg
import os
import cv2
import numpy as np
from ultralytics import YOLO
import torch
import gc

class YoloCropper:
    def __init__(self, output_size=256, expansion_factor=0.5):
        self.output_size = output_size
        self.expansion_factor = expansion_factor

    def crop(self, image, box):
        # 박스 좌표를 정수로 변환
        x1, y1, x2, y2 = map(int, box)

        # 얼굴 영역의 너비와 높이 계산
        face_w = x2 - x1
        face_h = y2 - y1

        # 박스를 확장하기 위해 가로, 세로 길이 중 더 큰 값을 사용하여 정사각형을 만들기
        max_dim = max(face_w, face_h)
        expansion_amount = int(max_dim * self.expansion_factor)
        
        x1 = x1 - expansion_amount
        y1 = y1 - expansion_amount
        x2 = x2 + expansion_amount
        y2 = y2 + expansion_amount

        # 확장 후 경계를 넘는지 확인하고 조정
        if x1 < 0:
            x2 = min(image.shape[1], x2 + (-x1))
            x1 = 0
        if y1 < 0:
            y2 = min(image.shape[0], y2 + (-y1))
            y1 = 0
        if x2 > image.shape[1]:
            x1 = max(0, x1 - (x2 - image.shape[1]))
            x2 = image.shape[1]
        if y2 > image.shape[0]:
            y1 = max(0, y1 - (y2 - image.shape[0]))
            y2 = image.shape[0]

        # 확장 후 사각형이 아닌 경우 정사각형으로 맞추기
        new_w = x2 - x1
        new_h = y2 - y1

        if new_w > new_h:
            pad_top = (new_w - new_h) // 2
            pad_bottom = new_w - new_h - pad_top
            y1 = max(0, y1 - pad_top)
            y2 = min(image.shape[0], y2 + pad_bottom)
        elif new_h > new_w:
            pad_left = (new_h - new_w) // 2
            pad_right = new_h - new_w - pad_left
            x1 = max(0, x1 - pad_left)
            x2 = min(image.shape[1], x2 + pad_right)

        # 얼굴 영역 크롭
        cropped_face = image[y1:y2, x1:x2]

        # 지정된 크기로 리사이즈
        resized_face = cv2.resize(cropped_face, (self.output_size, self.output_size), interpolation=cv2.INTER_AREA)

        return resized_face, (y1, y2, x1, x2)

    def get_crop_coords(self, frame):
        # 얼굴을 검출하고 크롭 좌표를 반환하는 함수 (첫 프레임에서 사용)
        results = YOLO("pretrained_weights/yolov8n-face.pt")(frame)
        boxes = results[0].boxes.xyxy.tolist()

        if boxes:
            largest_face = max(boxes, key=lambda box: (box[2]-box[0]) * (box[3]-box[1]))
            return largest_face
        else:
            return None

def detect_and_crop_faces(image_path, cropper):
    model = YOLO("pretrained_weights/yolov8n-face.pt")
    results = model(image_path)
    cv2.imwrite("result/video_tmp/face.png", image_path)
    img = cv2.imread("result/video_tmp/face.png")
    # img = cv2.imread(image_path)
    boxes = results[0].boxes.xyxy.tolist()
    
    # 가장 큰 얼굴을 선택
    if boxes:
        largest_face = max(boxes, key=lambda box: (box[2]-box[0]) * (box[3]-box[1]))
        cropped_face , _ = cropper.crop(img, largest_face)
    else:
        cropped_face = None

    del model
    gc.collect()
    torch.cuda.empty_cache()
    torch.cuda.ipc_collect()

    return cropped_face


def process_video(video_path, output_path, cropper):
    model = YOLO("pretrained_weights/yolov8n-face.pt")
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error opening video stream or file")
        return
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  
    out = cv2.VideoWriter(output_path, fourcc, fps, (cropper.output_size, cropper.output_size))
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        results = model(frame)
        boxes = results[0].boxes.xyxy.tolist()

        if boxes:
            largest_face = max(boxes, key=lambda box: (box[2]-box[0]) * (box[3]-box[1]))
            cropped_face, _  = cropper.crop(frame, largest_face)
        else:
            cropped_face = None
        
        if cropped_face is not None:
            out.write(cropped_face)
    cap.release()
    out.release()

    del model
    gc.collect()
    torch.cuda.empty_cache()
    torch.cuda.ipc_collect()

    return output_path

def process_crop_video(input_video_path, process_method, face_per):
    print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
    print("video input name : ", input_video_path)
    print("video process method : ", process_method)
    print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
    output_video_path = "result/video_tmp/output_video.mp4"
    cropper = YoloCropper(output_size=512,expansion_factor=face_per)

    if process_method == 1:
        result_path = process_video(input_video_path, output_video_path, cropper)
        return result_path   , result_path  
    else:
        result_path = process_crop_video_fixed(input_video_path, output_video_path , cropper)
        return result_path   , result_path  


# cropper = Cropper(height=256, width=256)
# cropper = YoloCropper(output_size=512, expansion_factor=0.5)

def crop_and_merge_audio(input_video_path, output_video_path, crop_coords):
    # 크롭된 비디오의 임시 파일 경로
    temp_video_path = "result/video_tmp/temp_cropped_video.mp4"
    temp_audio_path = "result/video_tmp/temp_audio.aac"
    
    # 폴더 생성 로직 한 줄로 표현
    for path in [temp_video_path, temp_audio_path, output_video_path]:
        os.makedirs(os.path.dirname(path), exist_ok=True)

    y1, y2, x1, x2 = crop_coords
    crop_width = x2 - x1
    crop_height = y2 - y1
    x = x1
    y = y1

    # Debug: 좌표와 크기 값을 출력
    print(f"Crop Coordinates: {crop_coords}")
    print(f"Crop Width: {crop_width}, Crop Height: {crop_height}")
    print(f"X: {x}, Y: {y}")

    try:
        # 1. 비디오 크롭 및 저장 (오디오 제외)
        try:
            ffmpeg.input(input_video_path).filter('crop', w=crop_width, h=crop_height, x=x, y=y).output(temp_video_path, vcodec='libx264', an=None).overwrite_output().run(capture_stdout=True, capture_stderr=True)
        except ffmpeg.Error as e:
            print(f"Error during video cropping: {e.stderr.decode('utf-8')}")
            return

        # 2. 원본 비디오에서 오디오 추출
        try:
            ffmpeg.input(input_video_path).output(temp_audio_path, acodec='copy').overwrite_output().run(capture_stdout=True, capture_stderr=True)
        except ffmpeg.Error as e:
            print(f"Error during audio extraction: {e.stderr.decode('utf-8')}")
            return

        # 3. 크롭된 비디오와 원본 오디오를 합쳐서 최종 비디오 생성
        try:
            video = ffmpeg.input(temp_video_path)
            audio = ffmpeg.input(temp_audio_path)
            ffmpeg.output(video, audio, output_video_path, vcodec='copy', acodec='copy').overwrite_output().run(capture_stdout=True, capture_stderr=True)
        except ffmpeg.Error as e:
            print(f"Error during video and audio merging: {e.stderr.decode('utf-8')}")
            return

    finally:
        # 임시 파일 삭제
        if os.path.exists(temp_video_path):
            os.remove(temp_video_path)
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
    
    # 최종 출력 비디오 파일 경로 반환
    return output_video_path

def process_crop_video_fixed(input_video_path , output_video_path , cropper):
    cap = cv2.VideoCapture(input_video_path)
    
    ret, frame = cap.read()
    if not ret:
        return "Failed to read the first frame."
    
    # 첫 프레임에서 크롭된 이미지와 좌표를 얻음
    _, crop_coords = cropper.crop(frame, cropper.get_crop_coords(frame))
        
    if not crop_coords:
        return "No face detected, video not cropped."

    # 첫 프레임에서 얻은 크롭 좌표로 전체 비디오를 크롭 및 병합
    output_video_path = crop_and_merge_audio(input_video_path, output_video_path, crop_coords)
    return output_video_path

    
def yolocrop(frame, cropper):
    cropped_image = detect_and_crop_faces(frame, cropper)
    return cropped_image

def get_video_frame_total(video_path: str) -> int:
    capture = cv2.VideoCapture(video_path)
    video_frame_total = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    capture.release()
    return video_frame_total

def get_video_frame(video_path: str, frame_number: int) -> Optional[np.ndarray]:
    capture = cv2.VideoCapture(video_path)
    frame_total = capture.get(cv2.CAP_PROP_FRAME_COUNT)
    capture.set(cv2.CAP_PROP_POS_FRAMES, min(frame_total, frame_number - 1))
    has_frame, frame = capture.read()
    capture.release()
    if has_frame:
        return frame
    return None

def process_frame(video_path, frame_number,face_per):
    cropper = YoloCropper(output_size=512, expansion_factor=0.5)
    frame = get_video_frame(video_path, frame_number  )
    if frame is not None:
        # cropped_frame, _ = autocrop(frame)
        cropper.expansion_factor = face_per
        cropped_frame = yolocrop(frame, cropper)

        temp_dir = "result/video_tmp/"
        os.makedirs(temp_dir, exist_ok=True)
        temp_image_path = os.path.join(temp_dir, f"frame_{frame_number}.png")

        cropped_frame_rgb = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2RGB)
        cv2.imwrite(temp_image_path, cropped_frame_rgb)
        cv2.imwrite(temp_image_path, cropped_frame)
        # cropped_frame_rgb = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2RGB)
        return cropped_frame_rgb , temp_image_path

        return cropped_frame , temp_image_path
        return Image.fromarray(cropped_frame_rgb)
        return cropped_frame_rgb
    return None

def on_video_upload(video_path):
    print("비디오 경로 : ", video_path)
    total_frames = get_video_frame_total(video_path)
    # 슬라이더의 최대값을 total_frames - 1로 설정하고, 최소값은 0으로, 시작 값을 0으로 설정
    return gr.update(maximum=total_frames - 1, value=0), gr.update(visible=True, value=0)

# Gradio 인터페이스 정의
def video_edit_tab():
        
    with gr.Tab("비디오 편집"):
        with gr.Row():
            with gr.Column(scale=1 , min_width=200):
                video_input = gr.Video(label="Input Video")
                frame_slider = gr.Slider(minimum=0, maximum=100, step=1, value= 1, label="Frame Slider", visible=False)
                face_slider = gr.Slider(minimum=0, maximum=1, step=0.1, value=0.5, label="얼굴 비율")
            
            with gr.Column(scale=1 , min_width=200):
                crop_output = gr.Image()
                crop_video_bt = gr.Button("정사각형 비디오 생성")
                crop_version_radio = gr.Radio(label="비디오 타입",choices=[("고정",0),("움직이는",1)], value=0)
                crop_output_down = gr.File()
            with gr.Column(scale=1 , min_width=200):
                video_output = gr.Video(label="Output Video" , interactive=False)
                crop_video_output_down = gr.File()


        video_input.upload(on_video_upload, inputs=video_input, outputs=[frame_slider, frame_slider])
        frame_slider.change(process_frame, inputs=[video_input, frame_slider, face_slider], outputs=[crop_output, crop_output_down])
        crop_video_bt.click(fn=process_crop_video, inputs=[video_input, crop_version_radio, face_slider], outputs=[video_output, crop_video_output_down])
