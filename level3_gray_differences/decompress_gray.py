# File: decompress_gray_diff.py

from LZW_gray_diff import LZWGrayDiffCoding

def main():
    filename = "sample_gray"
    lzw = LZWGrayDiffCoding(filename)
    lzw.decompress_image_file()

if __name__ == "__main__":
    main()
