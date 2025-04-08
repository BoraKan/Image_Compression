# File: basic_image_ops.py

import os
from PIL import Image
import numpy as np

def read_image_color(img_path):
    """
    Verilen dosya yolundan renkli (RGB) bir PIL image oku.
    Farklı format olsa bile .convert('RGB') ile 3 kanala indirger.
    Return: (img, width, height)
    """
    img = Image.open(img_path).convert('RGB')
    width, height = img.size
    return img, width, height

def write_image_color(rgb_array, out_path):
    """
    3 kanallı numpy array'i (height x width x 3, dtype=uint8)
    PIL image'e dönüştürüp .bmp olarak kaydeder.
    """
    pil_img = Image.fromarray(rgb_array.astype(np.uint8), mode='RGB')
    pil_img.save(out_path, 'bmp')

def image_to_array_rgb(img):
    """
    RGB bir PIL Image'i numpy array'e çevirir.
    shape: (height, width, 3)
    Return: (np_array, width, height)
    """
    np_img = np.array(img)  # shape: (height, width, 3)
    height, width, channels = np_img.shape
    return np_img, width, height

def separate_rgb_channels(np_img):
    """
    (height, width, 3) array'den R, G, B kanallarını (1D flatten) döndür.
    R, G, B her biri shape (width*height,)
    """
    import numpy as np
    # R: np_img[:,:,0], G: np_img[:,:,1], B: np_img[:,:,2]
    R = np_img[:,:,0].flatten()
    G = np_img[:,:,1].flatten()
    B = np_img[:,:,2].flatten()
    return R, G, B

def combine_rgb_channels(R, G, B, width, height):
    """
    R, G, B 1D array'lerini (width*height,) -> (height, width, 3) birleştirir.
    Return: (height, width, 3) numpy array
    """
    import numpy as np
    size = width*height
    if len(R) != size or len(G) != size or len(B) != size:
        raise ValueError("R,G,B boyutları width*height ile eşleşmiyor!")
    # 2D'ye reshape
    R_2d = R.reshape((height, width))
    G_2d = G.reshape((height, width))
    B_2d = B.reshape((height, width))
    # 3 kanalı birleştir
    rgb = np.dstack((R_2d, G_2d, B_2d)).astype(np.uint8)
    return rgb
