# File: decompress_color_diff.py

from LZW_color_diff import LZWColorDiffCoding

def main():
    filename = "sample_color"  # => sample_color_color_diff.bin girdi
    coder = LZWColorDiffCoding(filename)
    coder.decompress_image_file()

if __name__ == "__main__":
    main()
