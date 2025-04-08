# File: compress_gray_diff.py

from LZW_gray_diff import LZWGrayDiffCoding

def main():
    filename = "sample_gray"  # => sample_gray.bmp
    lzw = LZWGrayDiffCoding(filename)
    lzw.compress_image_file()

if __name__ == "__main__":
    main()
