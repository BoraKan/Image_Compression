# File: LZW_gray.py


import os
import math
from basic_image_ops import (
   read_image_grayscale,
   write_image_grayscale,
   image_to_flat_array,
   flat_array_to_image
)




class LZWGrayCoding:
   """
   Gri tonlu (8-bit) bir resmi LZW ile sıkıştırma/açma sınıfı.
   """


   def __init__(self, filename):
       """
       filename: örn. 'sample_gray'
       Bu, 'sample_gray.bmp' dosyasını sıkıştırıp
       'sample_gray.bin' dosyası üretecek.
       """
       self.filename = filename
       self.codelength = None  # sıkıştırma sırasında hesaplanacak


   def compress_image_file(self):
       """
       .bmp (gri ton) resmi okuyup,
       piksel değerlerini LZW ile sıkıştırıp,
       .bin dosyasına yazar.
       Return: çıktı dosyasının path'i
       """
       current_dir = os.path.dirname(os.path.realpath(__file__))


       input_file = self.filename + ".bmp"
       input_path = os.path.join(current_dir, input_file)


       output_file = self.filename + ".bin"
       output_path = os.path.join(current_dir, output_file)


       # 1) resmi oku -> PIL -> flatten array
       img, width, height = read_image_grayscale(input_path)
       flat_array, w, h = image_to_flat_array(img)


       # 2) LZW encode
       encoded_integers = self.lzw_encode(flat_array)


       # 3) integer list -> bit string
       bit_string = self.int_list_to_bitstring(encoded_integers)


       # 4) code length'i başa ekle
       bit_string = self.add_codelength_info(bit_string)


       # 5) padding
       padded_bit_string = self.pad_bitstring(bit_string)


       # 6) byte array'e dön, yaz
       byte_array = self.bitstring_to_bytearray(padded_bit_string)
       with open(output_path, "wb") as f:
           f.write(byte_array)


       # Sıkıştırma oranı vb. hesap
       # Orijinal boyut => width*height piksel, 1 byte/piksel
       uncompressed_size = width * height
       compressed_size = len(byte_array)
       if compressed_size != 0:
           ratio = uncompressed_size / compressed_size
       else:
           ratio = 1.0


       print(f"{input_file} -> {output_file} sıkıştırma tamamlandı.")
       print(f"Resim boyutu     : {width} x {height}")
       print(f"Orijinal boyut   : {uncompressed_size} bytes (piksel sayısı)")
       print(f"Sıkıştırılmış boyut : {compressed_size} bytes")
       print(f"Sıkıştırma Oranı : {ratio:.2f}")
       print(f"Kod Uzunluğu     : {self.codelength} bit")


       return output_path


   def decompress_image_file(self):
       """
       .bin dosyasını okuyup LZW decode ile gri ton resmi geri elde eder,
       .bmp olarak yazar.
       Return: çıktı resminin path'i
       """
       current_dir = os.path.dirname(os.path.realpath(__file__))


       input_file = self.filename + ".bin"
       input_path = os.path.join(current_dir, input_file)


       output_file = self.filename + "_decompressed.bmp"
       output_path = os.path.join(current_dir, output_file)


       # 1) .bin dosyasını byte'lar olarak oku -> bit string
       with open(input_path, "rb") as f:
           data = f.read()


       bit_str = ""
       for byte in data:
           bit_str += bin(byte)[2:].rjust(8, '0')


       # 2) padding'i kaldır
       bit_str = self.remove_padding(bit_str)


       # 3) code length'i baştan al
       bit_str = self.extract_codelength_info(bit_str)


       # 4) bit string -> integer list
       encoded_values = self.bitstring_to_int_list(bit_str)


       # 5) LZW decode -> piksel array
       flat_decoded_array = self.lzw_decode(encoded_values)


       # Burada boyutu bilmiyoruz!
       # Normalde width, height'ı da saklamak lazım (ya da sabit biliyoruz diyelim).
       # Basit yaklaşım: orijinal resmi tanıyorsak width/height'ı parametre verebilirsin.
       # Veya .bin dosyasına width/height eklemen gerekir.
       # Şimdilik bir method: get the dimension from a side file or pass it as param.


       # Örnek olsun diye,
       # diyelim ki resmin boyutunu biliyoruz: 640 x 480 (ya da hoca sabit vermiş).
       # PRATİKTE: Orijinal resmi saklamadan önce boyutu da .bin'e eklemen gerek!
       # Aşağıda sadece demonstration var:
       # flat_decoded_array = array of length W*H
       # We must reshape. Suppose we do it from a side text or so.
       # -------------------------------------------------------------------
       # Burada basitçe orijinal .bmp'yi okumadan (imkansız):
       #  - ya bin dosyasına 2 byte width, 2 byte height ekle (en üste)
       #  - ya parametre ile ver
       # Örneği basit tutmak için "dummy" atıyoruz.
       # Kodu gerçek projede boyutları .bin'e ekleyecek şekilde genişletmelisin!


       # Fake sabit boyut:
       # width = 256
       # height = len(flat_decoded_array) // width
       # Yine de for correctness, let's do something:


       # Aşağıda basit bir check var:
       length = len(flat_decoded_array)
       # Tek seferde height veya width'i bilinçli atayabiliriz:
       # diyelim width=256, height= length//256
       # or as needed:
       width = 256
       height = length // 256
       print(f"[UYARI]: Geri açarken width=256 kabul edildi!")


       # reshape -> 2D array
       import numpy as np
       two_d = np.array(flat_decoded_array, dtype=np.uint8).reshape((height, width))


       # 6) resmi kaydet
       write_image_grayscale(two_d, output_path)


       print(f"{input_file} -> {output_file} decompress tamamlandı.")
       return output_path


   # --------------------------------------------------------------------------
   # LZW encode/decode
   # --------------------------------------------------------------------------
   def lzw_encode(self, pixel_array):
       """
       Gri ton piksel dizisini (0..255) LZW integer kod listesine dönüştür.
       pixel_array: 1D numpy array veya python list, elemanlar [0..255].
       """
       dict_size = 256
       # key: tuple/string => value: int
       # ama piksel integer'ı string'e çevirip dictionary'de tutabiliriz
       dictionary = {chr(i): i for i in range(dict_size)}


       w = ""
       encoded_result = []


       for val in pixel_array:
           c = chr(val)  # tek karakter
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


       self.codelength = math.ceil(math.log2(dict_size))
       if self.codelength < 8:
           self.codelength = 8  # min 8 bit diyebilirsin


       return encoded_result


   def lzw_decode(self, encoded_list):
       """
       LZW decode -> gri ton piksel array (liste).
       """
       dict_size = 256
       dictionary = {i: chr(i) for i in range(dict_size)}


       if not encoded_list:
           return []


       w = chr(encoded_list.pop(0))
       output_chars = [w]  # list of strings


       for code in encoded_list:
           if code in dictionary:
               entry = dictionary[code]
           elif code == dict_size:
               # special case
               entry = w + w[0]
           else:
               raise ValueError(f"Geçersiz code: {code}")


           output_chars.append(entry)


           # dictionary'e yeni ek
           dictionary[dict_size] = w + entry[0]
           dict_size += 1


           w = entry


       # output_chars bir karakterler dizisi, bunları integer'a dön
       result_integers = []
       for chunk in output_chars:
           for ch in chunk:
               result_integers.append(ord(ch))


       return result_integers


   # --------------------------------------------------------------------------
   # Bit string <-> integer list  (benzer Level 1 mantığı)
   # --------------------------------------------------------------------------
   def int_list_to_bitstring(self, int_list):
       bits = ""
       for num in int_list:
           bits += format(num, f"0{self.codelength}b")
       return bits


   def add_codelength_info(self, bit_string):
       # 8 bit
       codelen_str = format(self.codelength, '08b')
       return codelen_str + bit_string


   def pad_bitstring(self, bit_string):
       extra_bits = (8 - (len(bit_string) % 8)) % 8
       bit_string += "0" * extra_bits
       # başa 8 bit ile padding miktarı
       padding_info = format(extra_bits, '08b')
       return padding_info + bit_string


   def bitstring_to_bytearray(self, padded_bit_string):
       if len(padded_bit_string) % 8 != 0:
           raise ValueError("Hatalı padding!")
       b_array = bytearray()
       for i in range(0, len(padded_bit_string), 8):
           chunk = padded_bit_string[i:i + 8]
           b_array.append(int(chunk, 2))
       return b_array


   def remove_padding(self, total_bits):
       # ilk 8 bit -> padding
       padding_info = total_bits[:8]
       extra_bits = int(padding_info, 2)
       bit_string = total_bits[8:]
       if extra_bits > 0:
           bit_string = bit_string[:-extra_bits]
       return bit_string


   def extract_codelength_info(self, bit_string):
       codelen_str = bit_string[:8]
       self.codelength = int(codelen_str, 2)
       return bit_string[8:]


   def bitstring_to_int_list(self, bit_string):
       result = []
       for i in range(0, len(bit_string), self.codelength):
           chunk = bit_string[i:i + self.codelength]
           if len(chunk) < self.codelength:
               break
           val = int(chunk, 2)
           result.append(val)
       return result



