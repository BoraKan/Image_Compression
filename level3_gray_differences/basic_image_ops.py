# File: basic_image_ops.py

import os
from PIL import Image
import numpy as np

def read_image_grayscale(img_path):
    """
    Verilen dosya yolundan gri tonlu (L mode) bir PIL image oku.
    Girdi renkli olsa bile .convert('L') ile griye çevirir.
    Return: (img, width, height)  [PIL image, en, boy]
    """
    img = Image.open(img_path).convert('L')
    width, height = img.size
    return img, width, height

def write_image_grayscale(img_array, out_path):
    """
    Numpy array'i (tek kanallı, 0-255) PIL'e çevirip .bmp olarak kaydeder.
    """
    pil_img = Image.fromarray(img_array.astype(np.uint8), mode='L')
    pil_img.save(out_path, 'bmp')

def image_to_flat_array(img):
    """
    Gri tonlu bir PIL Image objesini numpy array'e dönüştürüp flatten (1D) eder.
    Return: (flat_array, width, height)
    """
    np_img = np.array(img)  # shape: (height, width)
    height, width = np_img.shape
    flat_array = np_img.flatten()  # (width*height,) tek boyut
    return flat_array, width, height

def flat_array_to_image(flat_array, width, height):
    """
    1D bir piksel dizisini (0..255) -> (height, width) 2D numpy array.
    """
    import numpy as np
    two_d = np.reshape(flat_array, (height, width))
    return two_d
