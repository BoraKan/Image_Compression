# File: LZW_gray_diff.py

import os
import math
from basic_image_ops import (
    read_image_grayscale,
    write_image_grayscale,
    image_to_flat_array,
    flat_array_to_image
)

class LZWGrayDiffCoding:
    """
    Gri tonlu resimde satır bazında fark (difference) alarak LZW ile sıkıştırma/açma.
    """
    def __init__(self, filename):
        self.filename = filename
        self.codelength = None

    # --------------------------------------------------------------------------
    # 1) Ana Fonksiyon: compress_image_file
    # --------------------------------------------------------------------------
    def compress_image_file(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))

        input_file = self.filename + ".bmp"
        input_path = os.path.join(current_dir, input_file)

        output_file = self.filename + "_diff.bin"
        output_path = os.path.join(current_dir, output_file)

        # 1) Resmi oku -> flatten array
        img, width, height = read_image_grayscale(input_path)
        flat_array, w, h = image_to_flat_array(img)

        # 2) Fark dizisini oluştur
        diff_array = self.compute_difference_array(flat_array, w, h)

        # 3) LZW encode
        encoded_ints = self.lzw_encode(diff_array)

        # 4) integer list -> bit string
        bit_string = self.int_list_to_bitstring(encoded_ints)

        # 5) code length'i başa ekle
        bit_string = self.add_codelength_info(bit_string)

        # 6) padding
        padded_bits = self.pad_bitstring(bit_string)

        # 7) byte array'e çevir, dosyaya yaz
        byte_array = self.bitstring_to_bytearray(padded_bits)
        with open(output_path, "wb") as f:
            f.write(byte_array)

        # Bilgi
        uncompressed_size = w * h  # 1 byte/piksel
        compressed_size = len(byte_array)
        if compressed_size != 0:
            ratio = uncompressed_size / compressed_size
        else:
            ratio = 1.0
        print(f"{input_file} -> {output_file} (Difference + LZW) sıkıştırma tamam.")
        print(f"Resim boyutu      : {w} x {h}")
        print(f"Orijinal boyut    : {uncompressed_size} bytes")
        print(f"Sıkıştırılmış boyut : {compressed_size} bytes")
        print(f"Sık. Oranı        : {ratio:.2f}")
        print(f"Kod uzunluğu (bit): {self.codelength}")

        return output_path

    # --------------------------------------------------------------------------
    # 2) Decompress: .bin -> fark array -> orijinal piksel array -> .bmp
    # --------------------------------------------------------------------------
    def decompress_image_file(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))

        input_file = self.filename + "_diff.bin"
        input_path = os.path.join(current_dir, input_file)

        output_file = self.filename + "_diff_decompressed.bmp"
        output_path = os.path.join(current_dir, output_file)

        # 1) .bin'i oku -> bit string
        with open(input_path, "rb") as f:
            data = f.read()

        bit_str = ""
        for byte in data:
            bit_str += bin(byte)[2:].rjust(8, '0')

        # 2) padding'i kaldır
        bit_str = self.remove_padding(bit_str)

        # 3) codelength'i al
        bit_str = self.extract_codelength_info(bit_str)

        # 4) bit string -> integer list
        encoded_list = self.bitstring_to_int_list(bit_str)

        # 5) LZW decode -> fark array
        diff_array = self.lzw_decode(encoded_list)

        # 6) Fark array'den orijinal piksel array'i reconstruct
        #    Boyutları nasıl bileceğiz?
        #    (Aynı Level 2 sorun: width & height saklanmalı veya sabit.)
        # Örnek: sabit bir width=256 diyelim:
        length = len(diff_array)
        width = 256
        height = length // width
        print(f"[UYARI] decode sırasında width={width}, height={height} varsayıldı!")

        reconstructed = self.reconstruct_from_difference(diff_array, width, height)

        # 7) resmi kaydet
        write_image_grayscale(reconstructed, output_path)

        print(f"{input_file} -> {output_file} fark + LZW decompress tamam.")
        return output_path

    # --------------------------------------------------------------------------
    # 3) Fark Hesaplama / Geri Alma
    # --------------------------------------------------------------------------
    def compute_difference_array(self, flat_array, width, height):
        import numpy as np

        # 1) Buraya eklenecek (flat_array'i zorla 0..255 aralığında tut):
        flat_array = flat_array.astype(np.uint8)

        diff = np.zeros_like(flat_array, dtype=np.uint8)
        total_pixels = width * height

        for row in range(height):
            row_start = row * width
            # satırın ilk pikseli => fark = kendi değeri
            diff[row_start] = flat_array[row_start]

            for col in range(1, width):
                idx = row_start + col
                left = flat_array[idx - 1]
                cur = flat_array[idx]

                # 2) Farkı alırken int() ile çalış, sonra % 256
                #    Değer asla 256 olmaz, 0..255 aralığına sabitlenir.
                d = (int(cur) - int(left)) % 256

                # 3) Sonucu da np.uint8 olarak diff dizisine koy
                diff[idx] = np.uint8(d)

        return diff

    def reconstruct_from_difference(self, diff_array, width, height):
        import numpy as np
        rec = np.zeros_like(diff_array, dtype=np.uint8)

        for row in range(height):
            row_start = row * width
            # ilk piksel
            rec[row_start] = diff_array[row_start]

            for col in range(1, width):
                idx = row_start + col
                left_original = int(rec[idx - 1])  # int'e çevir
                diff_val = int(diff_array[idx])  # int'e çevir

                # Burada python integer aritmetiğiyle %256 yap
                original_val = (left_original + diff_val) % 256

                # Sonuç 0..255 arası => güvenle np.uint8 yapabiliriz
                rec[idx] = np.uint8(original_val)

        rec_2d = rec.reshape((height, width))
        return rec_2d

    # --------------------------------------------------------------------------
    # 4) LZW Encode / Decode
    # --------------------------------------------------------------------------
    def lzw_encode(self, diff_array):
        """
        Fark array'ini (0..255) -> LZW integer list.
        """
        dict_size = 256
        dictionary = {chr(i): i for i in range(dict_size)}

        w = ""
        encoded_result = []
        for val in diff_array:
            c = chr(val)
            wc = w + c
            if wc in dictionary:
                w = wc
            else:
                encoded_result.append(dictionary[w])
                dictionary[wc] = dict_size
                dict_size += 1
                w = c

        if w != "":
            encoded_result.append(dictionary[w])

        self.codelength = max(8, math.ceil(math.log2(dict_size)))
        return encoded_result

    def lzw_decode(self, encoded_list):
        """
        LZW decode -> fark array (0..255).
        """
        dict_size = 256
        dictionary = {i: chr(i) for i in range(dict_size)}

        if not encoded_list:
            return []

        w = chr(encoded_list.pop(0))
        output_chars = [w]

        for code in encoded_list:
            if code in dictionary:
                entry = dictionary[code]
            elif code == dict_size:
                entry = w + w[0]
            else:
                raise ValueError(f"Geçersiz code: {code}")
            output_chars.append(entry)

            dictionary[dict_size] = w + entry[0]
            dict_size += 1
            w = entry

        # char dizisini integer'a çevir
        result_integers = []
        for chunk in output_chars:
            for ch in chunk:
                result_integers.append(ord(ch))

        return result_integers

    # --------------------------------------------------------------------------
    # 5) Bit string <-> integer list & padding (Level 2'dekine benzer)
    # --------------------------------------------------------------------------
    def int_list_to_bitstring(self, int_list):
        bits = ""
        for num in int_list:
            bits += format(num, f"0{self.codelength}b")
        return bits

    def add_codelength_info(self, bit_string):
        codelen_str = format(self.codelength, '08b')
        return codelen_str + bit_string

    def pad_bitstring(self, bit_string):
        extra = (8 - len(bit_string) % 8) % 8
        bit_string += "0" * extra
        padding_info = format(extra, '08b')
        return padding_info + bit_string

    def bitstring_to_bytearray(self, padded_bits):
        if len(padded_bits) % 8 != 0:
            raise ValueError("Padding hatalı!")
        b_array = bytearray()
        for i in range(0, len(padded_bits), 8):
            chunk = padded_bits[i:i+8]
            b_array.append(int(chunk, 2))
        return b_array

    def remove_padding(self, total_bits):
        padding_info = total_bits[:8]
        extra = int(padding_info, 2)
        bit_string = total_bits[8:]
        if extra > 0:
            bit_string = bit_string[:-extra]
        return bit_string

    def extract_codelength_info(self, bit_string):
        codelen_str = bit_string[:8]
        self.codelength = int(codelen_str, 2)
        return bit_string[8:]

    def bitstring_to_int_list(self, bit_string):
        result = []
        for i in range(0, len(bit_string), self.codelength):
            chunk = bit_string[i:i+self.codelength]
            if len(chunk) < self.codelength:
                break
            val = int(chunk, 2)
            result.append(val)
        return result
