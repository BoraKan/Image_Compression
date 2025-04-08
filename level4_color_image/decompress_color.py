# File: decompress_color.py

from LZW_color import LZWColorCoding

def main():
    filename = "sample_color"  # => sample_color_color.bin girdi
    coder = LZWColorCoding(filename)
    coder.decompress_image_file()

if __name__ == "__main__":
    main()
