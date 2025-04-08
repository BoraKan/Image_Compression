# File: LZW_color_diff.py

import os
import math
import numpy as np
from basic_image_ops import (
    read_image_color,
    write_image_color,
    image_to_array_rgb,
    separate_rgb_channels,
    combine_rgb_channels
)

class LZWColorDiffCoding:
    """
    Level 5: Renkli (RGB) resimde satır bazlı fark -> LZW sıkıştırma.
    """

    def __init__(self, filename):
        self.filename = filename
        self.codelength = None

    # --------------------------------------------------------------------------
    # compress_image_file
    # --------------------------------------------------------------------------
    def compress_image_file(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        input_file = self.filename + ".bmp"
        input_path = os.path.join(current_dir, input_file)

        output_file = self.filename + "_color_diff.bin"
        output_path = os.path.join(current_dir, output_file)

        # 1) resmi oku, R/G/B kanalları al
        img, width, height = read_image_color(input_path)
        np_img, w, h = image_to_array_rgb(img)
        R, G, B = separate_rgb_channels(np_img)

        # 2) fark dizileri
        R_diff = self.compute_diff_array(R, w, h)
        G_diff = self.compute_diff_array(G, w, h)
        B_diff = self.compute_diff_array(B, w, h)

        # 3) merge => R_diff+G_diff+B_diff
        merged_diff = np.concatenate([R_diff, G_diff, B_diff])  # 3*w*h uzunluğunda

        # 4) LZW encode
        encoded_vals = self.lzw_encode(merged_diff)

        # 5) integer -> bit string
        bit_str = self.int_list_to_bitstring(encoded_vals)

        # 6) code length'i başa ekle
        bit_str = self.add_codelength_info(bit_str)

        # 7) padding
        padded_bits = self.pad_bitstring(bit_str)

        # 8) .bin dosyasına width/height ve bit data
        header = bytearray()
        header.append(width & 0xFF)
        header.append((width >> 8) & 0xFF)
        header.append(height & 0xFF)
        header.append((height >> 8) & 0xFF)

        bit_data = self.bitstring_to_bytearray(padded_bits)

        final_data = header + bit_data

        with open(output_path, "wb") as f:
            f.write(final_data)

        # Bilgi
        uncompressed_size = w*h*3
        compressed_size = len(final_data)
        ratio = uncompressed_size / compressed_size if compressed_size>0 else 1.0
        print(f"{input_file} -> {output_file} (Color + Diff + LZW) sıkıştırma ok.")
        print(f"Orijinal boyut (byte): {uncompressed_size}")
        print(f"Sıkıştırılmış boyut: {compressed_size}")
        print(f"Sıkıştırma Oranı: {ratio:.2f}")
        print(f"Codelength: {self.codelength} bit")

        return output_path

    # --------------------------------------------------------------------------
    # decompress_image_file
    # --------------------------------------------------------------------------
    def decompress_image_file(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        input_file = self.filename + "_color_diff.bin"
        input_path = os.path.join(current_dir, input_file)

        output_file = self.filename + "_color_diff_decompressed.bmp"
        output_path = os.path.join(current_dir, output_file)

        # 1) .bin'i oku
        with open(input_path, "rb") as f:
            raw = f.read()

        if len(raw) < 4:
            raise ValueError("Geçersiz dosya! width/height byte yok.")

        width = raw[0] | (raw[1]<<8)
        height = raw[2] | (raw[3]<<8)

        bit_data = raw[4:]  # geri kalan bit verisi

        # byte -> bit string
        bit_str = ""
        for b in bit_data:
            bit_str += bin(b)[2:].rjust(8, '0')

        # 2) remove padding
        bit_str = self.remove_padding(bit_str)

        # 3) code length'i al
        bit_str = self.extract_codelength_info(bit_str)

        # 4) bit string -> integer list
        encoded_vals = self.bitstring_to_int_list(bit_str)

        # 5) decode -> merged_diff (R_diff + G_diff + B_diff)
        merged_diff = self.lzw_decode(encoded_vals)

        # 6) Ayır => R_diff, G_diff, B_diff
        size = width * height
        if len(merged_diff) != size*3:
            raise ValueError(f"Fark verisi boyutu uymuyor! Beklenen: {size*3}, bulduk: {len(merged_diff)}")

        R_diff = merged_diff[:size]
        G_diff = merged_diff[size:2*size]
        B_diff = merged_diff[2*size:3*size]

        # 7) farklardan orijinal R, G, B'yi reconstruct
        R_orig = self.reconstruct_from_diff(R_diff, width, height)
        G_orig = self.reconstruct_from_diff(G_diff, width, height)
        B_orig = self.reconstruct_from_diff(B_diff, width, height)

        # 8) birleştir => renkli resim => bmp yaz
        rgb = combine_rgb_channels(np.array(R_orig), np.array(G_orig), np.array(B_orig), width, height)
        write_image_color(rgb, output_path)

        print(f"{input_file} -> {output_file} (Color+Diff) decompress tamam.")
        return output_path

    # --------------------------------------------------------------------------
    # FARK (DIFFERENCE) FONKSİYONLARI
    # --------------------------------------------------------------------------
    def compute_diff_array(self, channel_array, width, height):
        """
        channel_array: 1D [0..255], boyutu width*height
        Satır bazında fark:
          - her satırın ilk pikseli => diff=orijinal
          - sonrakiler => (cur - left) % 256
        """
        channel_array = channel_array.astype(np.uint8)

        diff = np.zeros_like(channel_array, dtype=np.uint8)
        for row in range(height):
            row_start = row * width
            # ilk piksel
            diff[row_start] = channel_array[row_start]
            # geri kalanlar
            for col in range(1, width):
                idx = row_start + col
                left = int(channel_array[idx - 1])
                cur = int(channel_array[idx])
                d = (cur - left) % 256
                diff[idx] = np.uint8(d)

        return diff

    def reconstruct_from_diff(self, diff_array, width, height):
        """
        diff -> orijinal
         - ilk piksel => orijinal=diff
         - sonrakiler => (left_original + diff) % 256
        Return: 1D array (uint8)
        """
        rec = np.zeros_like(diff_array, dtype=np.uint8)
        for row in range(height):
            row_start = row * width
            rec[row_start] = diff_array[row_start]
            for col in range(1, width):
                idx = row_start + col
                left_original = int(rec[idx - 1])
                diff_val = int(diff_array[idx])
                val = (left_original + diff_val) % 256
                rec[idx] = np.uint8(val)

        return rec

    # --------------------------------------------------------------------------
    # LZW encode/decode
    # --------------------------------------------------------------------------
    def lzw_encode(self, arr_1d):
        dict_size = 256
        dictionary = {chr(i): i for i in range(dict_size)}

        w = ""
        result = []
        for val in arr_1d:
            c = chr(val)
            wc = w + c
            if wc in dictionary:
                w = wc
            else:
                result.append(dictionary[w])
                dictionary[wc] = dict_size
                dict_size += 1
                w = c

        if w != "":
            result.append(dictionary[w])

        self.codelength = max(8, math.ceil(math.log2(dict_size)))
        return result

    def lzw_decode(self, encoded):
        dict_size = 256
        dictionary = {i: chr(i) for i in range(dict_size)}

        if not encoded:
            return []

        w = chr(encoded.pop(0))
        out_chars = [w]

        for code in encoded:
            if code in dictionary:
                entry = dictionary[code]
            elif code == dict_size:
                entry = w + w[0]
            else:
                raise ValueError(f"Geçersiz LZW code: {code}")
            out_chars.append(entry)
            dictionary[dict_size] = w + entry[0]
            dict_size += 1
            w = entry

        result_integers = []
        for chunk in out_chars:
            for ch in chunk:
                result_integers.append(ord(ch))
        return result_integers

    # --------------------------------------------------------------------------
    # Bit string <-> int list, codelength & padding
    # --------------------------------------------------------------------------
    def int_list_to_bitstring(self, int_list):
        bits = ""
        for num in int_list:
            bits += format(num, f"0{self.codelength}b")
        return bits

    def add_codelength_info(self, bitstr):
        codelen_str = format(self.codelength, '08b')
        return codelen_str + bitstr

    def pad_bitstring(self, bitstr):
        extra = (8 - len(bitstr) % 8) % 8
        bitstr += "0" * extra
        pad_info = format(extra, '08b')
        return pad_info + bitstr

    def bitstring_to_bytearray(self, padded_bits):
        if len(padded_bits) % 8 != 0:
            raise ValueError("bitstring 8'e bölünemiyor.")
        ba = bytearray()
        for i in range(0, len(padded_bits), 8):
            chunk = padded_bits[i:i+8]
            ba.append(int(chunk, 2))
        return ba

    def remove_padding(self, total_bits):
        padding_info = total_bits[:8]
        extra = int(padding_info, 2)
        bit_string = total_bits[8:]
        if extra>0:
            bit_string = bit_string[:-extra]
        return bit_string

    def extract_codelength_info(self, bitstr):
        codelen_str = bitstr[:8]
        self.codelength = int(codelen_str, 2)
        return bitstr[8:]

    def bitstring_to_int_list(self, bitstr):
        ints = []
        for i in range(0, len(bitstr), self.codelength):
            chunk = bitstr[i:i+self.codelength]
            if len(chunk)<self.codelength:
                break
            val = int(chunk, 2)
            ints.append(val)
        return ints
