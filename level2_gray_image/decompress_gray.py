# File: decompress_gray.py

import os
from LZW_gray import LZWGrayCoding

def main():
    filename = "sample_gray"  # => 'sample_gray.bin' girdi
    lzw = LZWGrayCoding(filename)
    output_path = lzw.decompress_image_file()
    print(f"Açma (decompress) tamam. Çıktı: {output_path}")

if __name__ == "__main__":
    main()
