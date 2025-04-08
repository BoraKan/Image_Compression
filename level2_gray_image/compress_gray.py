# File: compress_gray.py

import os
from LZW_gray import LZWGrayCoding

def main():
    # Sıkıştırılacak gri ton resim (örnek: sample_gray.bmp)
    filename = "sample_gray"
    # => 'sample_gray.bmp' girdi, 'sample_gray.bin' çıktı
    lzw = LZWGrayCoding(filename)
    output_path = lzw.compress_image_file()
    print(f"Sıkıştırma tamam. Çıktı: {output_path}")

if __name__ == "__main__":
    main()
