# File: LZW_color.py

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

class LZWColorCoding:
    """
    Renkli (RGB) resmi LZW ile sıkıştırma/açma.
    Tek bir akışta R+G+B kanalları ardışık eklenerek encode edilir.
    (Level 4: Fark yok, saf LZW.)
    """

    def __init__(self, filename):
        self.filename = filename
        self.codelength = None

    def compress_image_file(self):
        """
        filename.bmp -> filename_color.bin
        Aşağıdaki adımları yapar:
         1) read_image_color -> (width, height)
         2) R,G,B flatten
         3) (width,height) 4 byte olarak .bin'e yaz
         4) R+G+B tek bir array haline getir => LZW encode => bit string
         5) padding + byte array => .bin
        Return: output path
        """
        current_dir = os.path.dirname(os.path.realpath(__file__))
        input_file = self.filename + ".bmp"
        input_path = os.path.join(current_dir, input_file)

        output_file = self.filename + "_color.bin"
        output_path = os.path.join(current_dir, output_file)

        # 1) Resmi oku
        img, width, height = read_image_color(input_path)
        np_img, w, h = image_to_array_rgb(img)

        # 2) Kanalları ayır
        R, G, B = separate_rgb_channels(np_img)  # 1D flatten
        # Tek birleştir => [R..., G..., B...]
        merged_channels = np.concatenate([R, G, B])  # boyut = 3*w*h

        # 3) LZW encode
        encoded = self.lzw_encode(merged_channels)

        # 4) integer list -> bit string
        bit_str = self.int_list_to_bitstring(encoded)

        # 5) codelength'i başa koy
        bit_str = self.add_codelength_info(bit_str)

        # 6) padding
        padded_bits = self.pad_bitstring(bit_str)

        # 7) Byte array'e dönüştürmeden önce,
        #    .bin'in en başına 4 byte (width, height) ekleyeceğiz.
        #    Bunu yapmak için "ek bir bytearray" oluşturup
        #    width,height'i 16'şar bit olarak yazabiliriz.
        #    Sonra asıl bit verisini ekleyebiliriz.
        #    Fakat bit verimiz string formatta, bu karmaşık.
        #
        # Kolay bir yöntem:
        #    - önce 4 byte'ı normal binary formda dosyaya yazarız
        #    - sonra padded_bits'i yazarız.
        #    => Yani final .bin:
        #         [2 byte width][2 byte height][bitstring]
        # decode aşamasında ilk 4 byte'ı okur, bitstring'i geri kalanını okur.
        #
        # Aşağıda bunu tek seferde yapabilmek için,
        #   "header_array" + "bit_data_array" birleştireceğiz.
        # (Ama python formatlar farklı: bit string -> byte array,
        #  4 byte -> normal int.)
        #
        # Step-by-step:
        # A) 4 byte => bytearray
        header_bytes = bytearray()
        # width ve height'i 2'şer byte (16 bit) little-endian yazalım:
        header_bytes.append(width & 0xFF)
        header_bytes.append((width >> 8) & 0xFF)
        header_bytes.append(height & 0xFF)
        header_bytes.append((height >> 8) & 0xFF)

        # B) bit data -> bytearray
        bit_data_array = self.bitstring_to_bytearray(padded_bits)

        # C) final array = header_bytes + bit_data_array
        final_array = header_bytes + bit_data_array

        # Dosyaya yaz
        with open(output_path, "wb") as f:
            f.write(final_array)

        # Bilgi
        uncompressed_size = w * h * 3  # 3 kanal => 1 byte per channel
        compressed_size = len(final_array)
        ratio = uncompressed_size / compressed_size if compressed_size>0 else 1.0
        print(f"{input_file} -> {output_file} sıkıştırma OK.")
        print(f"Resim boyutu : {w} x {h}")
        print(f"Orijinal boyut : {uncompressed_size} bytes (RGB piksel sayısı)")
        print(f"Sıkıştırılmış boyut: {compressed_size} bytes")
        print(f"Sıkıştırma Oranı: {ratio:.2f}")
        print(f"Codelength: {self.codelength} bit")
        return output_path

    def decompress_image_file(self):
        """
        filename_color.bin -> filename_color_decompressed.bmp
        """
        current_dir = os.path.dirname(os.path.realpath(__file__))
        input_file = self.filename + "_color.bin"
        input_path = os.path.join(current_dir, input_file)

        output_file = self.filename + "_color_decompressed.bmp"
        output_path = os.path.join(current_dir, output_file)

        # 1) .bin dosyasını oku
        with open(input_path, "rb") as f:
            all_data = f.read()

        # all_data => ilk 4 byte: width, height
        # geri kalanı bit verisi
        if len(all_data) < 4:
            raise ValueError("Dosya formatı hatalı. En az 4 byte lazım (width, height).")

        width = (all_data[0] | (all_data[1]<<8)) & 0xFFFF
        height = (all_data[2] | (all_data[3]<<8)) & 0xFFFF

        # print(f"Okunan width={width}, height={height}")

        # bit verisini 4. byte'tan itibaren okuyoruz
        bit_bytes = all_data[4:]  # geriye kalan
        # Byte -> bit string
        bit_str = ""
        for b in bit_bytes:
            bit_str += bin(b)[2:].rjust(8, '0')

        # 2) padding'i kaldır
        bit_str = self.remove_padding(bit_str)

        # 3) codelength'i çek
        bit_str = self.extract_codelength_info(bit_str)

        # 4) integer list
        encoded_list = self.bitstring_to_int_list(bit_str)

        # 5) decode -> merged array (R+G+B)
        merged_array = self.lzw_decode(encoded_list)  # length = width*height*3

        if len(merged_array) != width*height*3:
            raise ValueError(f"Kanal verisi boyutu uymuyor! Beklenen: {width*height*3}, bulduk: {len(merged_array)}")

        # 6) Ayrı R, G, B
        size = width*height
        R = merged_array[:size]
        G = merged_array[size:2*size]
        B = merged_array[2*size:3*size]

        # 7) Birleştir -> RGB array -> bmp yaz
        rgb = combine_rgb_channels(np.array(R), np.array(G), np.array(B), width, height)
        write_image_color(rgb, output_path)

        print(f"{input_file} -> {output_file} açma (decompress) OK.")
        return output_path

    # --------------------------------------------------------------------------
    # LZW encode/decode (benzer Level 2 & 3)
    # --------------------------------------------------------------------------
    def lzw_encode(self, array_1d):
        """
        array_1d: [0..255] integer (R, G veya B,
        veya R+G+B hepsi concatenated).
        """
        dict_size = 256
        dictionary = {chr(i): i for i in range(dict_size)}

        w = ""
        result = []

        for val in array_1d:
            c = chr(val)
            wc = w + c
            if wc in dictionary:
                w = wc
            else:
                result.append(dictionary[w])
                dictionary[wc] = dict_size
                dict_size += 1
                w = c

        if w:
            result.append(dictionary[w])

        self.codelength = max(8, math.ceil(math.log2(dict_size)))
        return result

    def lzw_decode(self, encoded_list):
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

        # karakter dizisini integer dizisine çevir
        result_integers = []
        for chunk in output_chars:
            for ch in chunk:
                result_integers.append(ord(ch))

        return result_integers

    # --------------------------------------------------------------------------
    # Bit string <-> int list, codelength/padding
    # --------------------------------------------------------------------------
    def int_list_to_bitstring(self, int_list):
        bits = ""
        for num in int_list:
            bits += format(num, f"0{self.codelength}b")
        return bits

    def add_codelength_info(self, bitstr):
        # 8 bit codelength
        codelen_bits = format(self.codelength, '08b')
        return codelen_bits + bitstr

    def pad_bitstring(self, bitstr):
        extra = (8 - len(bitstr) % 8) % 8
        bitstr += "0" * extra
        padding_info = format(extra, '08b')
        return padding_info + bitstr

    def bitstring_to_bytearray(self, padded_bits):
        if len(padded_bits) % 8 != 0:
            raise ValueError("bitstring 8'e bölünemiyor")
        ba = bytearray()
        for i in range(0, len(padded_bits), 8):
            chunk = padded_bits[i:i+8]
            ba.append(int(chunk, 2))
        return ba

    def remove_padding(self, total_bits):
        padding_info = total_bits[:8]
        extra = int(padding_info, 2)
        bit_string = total_bits[8:]
        if extra > 0:
            bit_string = bit_string[:-extra]
        return bit_string

    def extract_codelength_info(self, bitstr):
        codelen_bits = bitstr[:8]
        self.codelength = int(codelen_bits, 2)
        return bitstr[8:]

    def bitstring_to_int_list(self, bitstr):
        int_list = []
        for i in range(0, len(bitstr), self.codelength):
            chunk = bitstr[i:i+self.codelength]
            if len(chunk) < self.codelength:
                break
            val = int(chunk, 2)
            int_list.append(val)
        return int_list
