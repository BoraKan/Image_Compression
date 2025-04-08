# File: compress_color.py

from LZW_color import LZWColorCoding

def main():
    filename = "sample_color"  # => sample_color.bmp
    coder = LZWColorCoding(filename)
    coder.compress_image_file()

if __name__ == "__main__":
    main()
