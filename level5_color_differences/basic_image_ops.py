# File: basic_image_ops.py

import os
from PIL import Image
import numpy as np

def read_image_color(img_path):
    """
    Verilen dosya yolundan renkli (RGB) bir PIL image oku.
    .convert('RGB') ile 3 kanala çevirir.
    Return: (img, width, height)
    """
    img = Image.open(img_path).convert('RGB')
    width, height = img.size
    return img, width, height

def write_image_color(rgb_array, out_path):
    """
    3 kanallı numpy array (height x width x 3) => PIL => bmp kaydet
    """
    pil_img = Image.fromarray(rgb_array.astype(np.uint8), mode='RGB')
    pil_img.save(out_path, 'bmp')

def image_to_array_rgb(img):
    """
    PIL (RGB) => numpy array (height, width, 3)
    """
    np_img = np.array(img)  # shape: (H, W, 3)
    h, w, c = np_img.shape
    return np_img, w, h

def separate_rgb_channels(np_img):
    """
    (H, W, 3) => R, G, B 1D flatten
    """
    R = np_img[:,:,0].flatten()
    G = np_img[:,:,1].flatten()
    B = np_img[:,:,2].flatten()
    return R, G, B

def combine_rgb_channels(R, G, B, width, height):
    """
    1D R, G, B => (H, W, 3)
    """
    import numpy as np
    size = width * height
    R_2d = R.reshape((height, width))
    G_2d = G.reshape((height, width))
    B_2d = B.reshape((height, width))
    rgb = np.dstack((R_2d, G_2d, B_2d)).astype(np.uint8)
    return rgb
