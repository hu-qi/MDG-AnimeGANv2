import os
from unittest import result
import dlib
import collections
from typing import Union, List
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import cv2
import PIL.Image
import PIL.ImageFile
import numpy as np
import scipy.ndimage
import requests
import sys
sys.path.append("animegan2-pytorch")

import torch
torch.set_grad_enabled(False)
print(torch.__version__, torch.cuda.is_available())
from model import Generator

model_fname = "face_paint_512_v2_0.pt"

# model_urls = {
#     "face_paint_512_v0.pt": "https://drive.google.com/uc?id=1WK5Mdt6mwlcsqCZMHkCUSDJxN1UyFi0-",
#     "face_paint_512_v2_0.pt": "https://drive.google.com/uc?id=18H3iK09_d54qEDoWIc82SyWB2xun4gjU",
# }

device = "cpu"

model = Generator().eval().to(device)
model.load_state_dict(torch.load(model_fname))
from torchvision.transforms.functional import to_tensor, to_pil_image


def get_dlib_face_detector(predictor_path: str = "shape_predictor_68_face_landmarks.dat"):

    if not os.path.isfile(predictor_path):
        model_file = "shape_predictor_68_face_landmarks.dat.bz2"
        os.system(f"wget http://dlib.net/files/{model_file}")
        os.system(f"bzip2 -dk {model_file}")

    detector = dlib.get_frontal_face_detector()
    shape_predictor = dlib.shape_predictor(predictor_path)

    def detect_face_landmarks(img: Union[Image.Image, np.ndarray]):
        if isinstance(img, Image.Image):
            img = np.array(img)
        faces = []
        dets = detector(img)
        for d in dets:
            shape = shape_predictor(img, d)
            faces.append(np.array([[v.x, v.y] for v in shape.parts()]))
        return faces
    
    return detect_face_landmarks


def display_facial_landmarks(
    img: Image, 
    landmarks: List[np.ndarray],
    fig_size=[15, 15]
):
    plot_style = dict(
        marker='o',
        markersize=4,
        linestyle='-',
        lw=2
    )
    pred_type = collections.namedtuple('prediction_type', ['slice', 'color'])
    pred_types = {
        'face': pred_type(slice(0, 17), (0.682, 0.780, 0.909, 0.5)),
        'eyebrow1': pred_type(slice(17, 22), (1.0, 0.498, 0.055, 0.4)),
        'eyebrow2': pred_type(slice(22, 27), (1.0, 0.498, 0.055, 0.4)),
        'nose': pred_type(slice(27, 31), (0.345, 0.239, 0.443, 0.4)),
        'nostril': pred_type(slice(31, 36), (0.345, 0.239, 0.443, 0.4)),
        'eye1': pred_type(slice(36, 42), (0.596, 0.875, 0.541, 0.3)),
        'eye2': pred_type(slice(42, 48), (0.596, 0.875, 0.541, 0.3)),
        'lips': pred_type(slice(48, 60), (0.596, 0.875, 0.541, 0.3)),
        'teeth': pred_type(slice(60, 68), (0.596, 0.875, 0.541, 0.4))
    }

    fig = plt.figure(figsize=fig_size)
    ax = fig.add_subplot(1, 1, 1)
    ax.imshow(img)
    ax.axis('off')

    for face in landmarks:
        for pred_type in pred_types.values():
            ax.plot(
                face[pred_type.slice, 0],
                face[pred_type.slice, 1],
                color=pred_type.color, **plot_style
            )
    plt.show()


def align_and_crop_face(
    img: Image.Image,
    landmarks: np.ndarray,
    expand: float = 1.0,
    output_size: int = 1024, 
    transform_size: int = 4096,
    enable_padding: bool = True,
):
    # 将五官数据转为数组
    # pylint: disable=unused-variable
    lm = landmarks
    lm_chin          = lm[0  : 17]  # left-right
    lm_eyebrow_left  = lm[17 : 22]  # left-right
    lm_eyebrow_right = lm[22 : 27]  # left-right
    lm_nose          = lm[27 : 31]  # top-down
    lm_nostrils      = lm[31 : 36]  # top-down
    lm_eye_left      = lm[36 : 42]  # left-clockwise
    lm_eye_right     = lm[42 : 48]  # left-clockwise
    lm_mouth_outer   = lm[48 : 60]  # left-clockwise
    lm_mouth_inner   = lm[60 : 68]  # left-clockwise

    # 计算辅助向量
    eye_left     = np.mean(lm_eye_left, axis=0)
    eye_right    = np.mean(lm_eye_right, axis=0)
    eye_avg      = (eye_left + eye_right) * 0.5
    eye_to_eye   = eye_right - eye_left
    mouth_left   = lm_mouth_outer[0]
    mouth_right  = lm_mouth_outer[6]
    mouth_avg    = (mouth_left + mouth_right) * 0.5
    eye_to_mouth = mouth_avg - eye_avg

    # 提取矩形框
    x = eye_to_eye - np.flipud(eye_to_mouth) * [-1, 1] # flipud函数实现矩阵的上下翻转；数组乘法，每行对应位置相乘
    x /= np.hypot(*x)
    x *= max(np.hypot(*eye_to_eye) * 2.0, np.hypot(*eye_to_mouth) * 1.8)
    x *= expand
    y = np.flipud(x) * [-1, 1]
    c = eye_avg + eye_to_mouth * 0.1
    quad = np.stack([c - x - y, c - x + y, c + x + y, c + x - y])
    qsize = np.hypot(*x) * 2

    # 缩放
    shrink = int(np.floor(qsize / output_size * 0.5))
    if shrink > 1:
        rsize = (int(np.rint(float(img.size[0]) / shrink)), int(np.rint(float(img.size[1]) / shrink)))
        img = img.resize(rsize, PIL.Image.ANTIALIAS)
        quad /= shrink
        qsize /= shrink

    # 裁剪
    border = max(int(np.rint(qsize * 0.1)), 3)
    crop = (int(np.floor(min(quad[:,0]))), int(np.floor(min(quad[:,1]))), int(np.ceil(max(quad[:,0]))), int(np.ceil(max(quad[:,1]))))
    crop = (max(crop[0] - border, 0), max(crop[1] - border, 0), min(crop[2] + border, img.size[0]), min(crop[3] + border, img.size[1]))
    if crop[2] - crop[0] < img.size[0] or crop[3] - crop[1] < img.size[1]:
        img = img.crop(crop)
        quad -= crop[0:2]

    # 填充数据
    pad = (int(np.floor(min(quad[:,0]))), int(np.floor(min(quad[:,1]))), int(np.ceil(max(quad[:,0]))), int(np.ceil(max(quad[:,1]))))
    pad = (max(-pad[0] + border, 0), max(-pad[1] + border, 0), max(pad[2] - img.size[0] + border, 0), max(pad[3] - img.size[1] + border, 0))
    if enable_padding and max(pad) > border - 4:
        pad = np.maximum(pad, int(np.rint(qsize * 0.3)))
        img = np.pad(np.float32(img), ((pad[1], pad[3]), (pad[0], pad[2]), (0, 0)), 'reflect')
        h, w, _ = img.shape
        y, x, _ = np.ogrid[:h, :w, :1]
        mask = np.maximum(1.0 - np.minimum(np.float32(x) / pad[0], np.float32(w-1-x) / pad[2]), 1.0 - np.minimum(np.float32(y) / pad[1], np.float32(h-1-y) / pad[3]))
        blur = qsize * 0.02
        img += (scipy.ndimage.gaussian_filter(img, [blur, blur, 0]) - img) * np.clip(mask * 3.0 + 1.0, 0.0, 1.0)
        img += (np.median(img, axis=(0,1)) - img) * np.clip(mask, 0.0, 1.0)
        img = PIL.Image.fromarray(np.uint8(np.clip(np.rint(img), 0, 255)), 'RGB')
        quad += pad[:2]

    # 转化图片
    img = img.transform((transform_size, transform_size), PIL.Image.QUAD, (quad + 0.5).flatten(), PIL.Image.BILINEAR)
    if output_size < transform_size:
        img = img.resize((output_size, output_size), PIL.Image.ANTIALIAS)

    return img


def face2paint(
    img: Image.Image,
    size: int,
    side_by_side: bool = False,
) -> Image.Image:

    w, h = img.size
    s = min(w, h)
    img = img.crop(((w - s) // 2, (h - s) // 2, (w + s) // 2, (h + s) // 2))
    img = img.resize((size, size), Image.LANCZOS)

    input = to_tensor(img).unsqueeze(0) * 2 - 1
    output = model(input.to(device)).cpu()[0]

    if side_by_side:
        output = torch.cat([input[0], output], dim=2)

    output = (output * 0.5 + 0.5).clip(0, 1)

    return to_pil_image(output)

def load_image(image_path, x32=True):
    img = cv2.imread(image_path).astype(np.float32)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    h, w = img.shape[:2]
 
    if x32: # resize image to multiple of 32s
        def to_32s(x):
            return 256 if x < 256 else x - x%32
        img = cv2.resize(img, (to_32s(w), to_32s(h)))
 
    img = torch.from_numpy(img)
    img = img/127.5 - 1.0
    return img

def other2paint(filepath, savePath):
    image = load_image(filepath, True)
    # print(image)
    with torch.no_grad():
        input = image.permute(2, 0,1).unsqueeze(0).to('cpu')
        out = model(input, True).squeeze(0).permute(1, 2, 0).cpu().numpy()
        out = (out + 1)*127.5
        out = np.clip(out, 0, 255).astype(np.uint8)
    cv2.imwrite(savePath, cv2.cvtColor(out, cv2.COLOR_BGR2RGB))

def inference_from_file(filepath, savePath):
    img = ''
    print('filepath', filepath)
    if filepath.startswith("http"):
        img = Image.open(requests.get(filepath, stream=True).raw).convert("RGB")
    else:
        img = Image.open(filepath).convert("RGB")
    face_detector = get_dlib_face_detector()
    landmarks = face_detector(img)
    print(len(landmarks))
    if len(landmarks) > 0:
        for landmark in landmarks:
            face = align_and_crop_face(img, landmark, expand=1.3)
            result = face2paint(face, 512)
            result.save(savePath)
            # return result
    else:
        other2paint(filepath, savePath)

def inference_from_url(url, savePath):
    img = Image.open(requests.get(url, stream=True).raw).convert("RGB")

    face_detector = get_dlib_face_detector()
    landmarks = face_detector(img)

    if len(landmarks) > 0:
        for landmark in landmarks:
            face = align_and_crop_face(img, landmark, expand=1.3)
            result = face2paint(face, 512)
            result.save(savePath)
            # return result
    else:
        other2paint(url, savePath)
