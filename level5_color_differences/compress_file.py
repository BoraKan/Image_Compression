# File: compress_color_diff.py

from LZW_color_diff import LZWColorDiffCoding

def main():
    filename = "sample_color"  # => sample_color.bmp
    coder = LZWColorDiffCoding(filename)
    coder.compress_image_file()

if __name__ == "__main__":
    main()
