"""
Стеганографический движок StegoGhost
Реализация LSB с псевдослучайной выборкой пикселей
"""

import numpy as np
from PIL import Image
import hashlib
import struct
from typing import Tuple, Optional, List
import io


class StegoEngine:
    """Основной класс для внедрения и извлечения данных"""
    
    def __init__(self):
        self.supported_formats = {'.png', '.jpg', '.jpeg', '.webp'}
        self.max_message_length = 4096
        self.header_size = 4  # Размер заголовка для хранения длины сообщения
        self.debug = False  # Отключаем отладку
        
    def _generate_pixel_sequence(self, seed: bytes, total_pixels: int, needed_pixels: int, offset: int = 0) -> List[int]:
        """
        Генерирует псевдослучайную последовательность индексов пикселей
        на основе seed для равномерного распределения
        
        Args:
            seed: Seed для генерации
            total_pixels: Общее количество пикселей
            needed_pixels: Количество нужных пикселей
            offset: Смещение в последовательности
        """
        # Используем SHA-256 для генерации детерминированной последовательности
        seed_hash = hashlib.sha256(seed).digest()
        seed_int = int.from_bytes(seed_hash[:4], 'big')
        
        if self.debug:
            print(f"[DEBUG] Seed hash: {seed_hash.hex()[:16]}...")
            print(f"[DEBUG] Seed int: {seed_int}")
            print(f"[DEBUG] Total pixels: {total_pixels}, needed: {needed_pixels}, offset: {offset}")
        
        rng = np.random.RandomState(seed_int)
        
        # ВАЖНО: Всегда генерируем ВСЕ индексы для консистентности
        # Это гарантирует одинаковую последовательность независимо от offset
        all_pixel_indices = np.arange(total_pixels)
        rng.shuffle(all_pixel_indices)
        
        # Берем нужную часть с учетом offset
        start_idx = offset
        end_idx = offset + needed_pixels
        
        if end_idx > total_pixels:
            raise ValueError(f"Недостаточно пикселей: нужно {end_idx}, доступно {total_pixels}")
        
        # ВАЖНО: НЕ сортируем индексы, чтобы сохранить последовательность
        result = all_pixel_indices[start_idx:end_idx].tolist()
        
        if self.debug and len(result) <= 5:
            print(f"[DEBUG] Indices (offset {offset}): {result}")
        elif self.debug:
            print(f"[DEBUG] First 5 indices (offset {offset}): {result[:5]}")
        
        return result
    
    def _bits_to_bytes(self, bits: List[int]) -> bytes:
        """Преобразует список битов в байты"""
        bytes_data = bytearray()
        for i in range(0, len(bits), 8):
            byte_bits = bits[i:i+8]
            if len(byte_bits) < 8:
                byte_bits.extend([0] * (8 - len(byte_bits)))
            byte_val = sum(bit << (7 - j) for j, bit in enumerate(byte_bits))
            bytes_data.append(byte_val)
        return bytes(bytes_data)
    
    def _bytes_to_bits(self, data: bytes) -> List[int]:
        """Преобразует байты в список битов"""
        bits = []
        for byte in data:
            for i in range(7, -1, -1):
                bits.append((byte >> i) & 1)
        return bits
    
    def embed_data(self, image_path: str, data: bytes, password: str) -> Image.Image:
        """
        Внедряет зашифрованные данные в изображение
        
        Args:
            image_path: Путь к исходному изображению
            data: Зашифрованные данные для внедрения
            password: Пароль для генерации seed
            
        Returns:
            Модифицированное изображение
        """
        if self.debug:
            print(f"\n[DEBUG EMBED] Starting embedding...")
            print(f"[DEBUG EMBED] Data length: {len(data)} bytes")
            print(f"[DEBUG EMBED] Password: {password}")
        
        # Загружаем изображение
        img = Image.open(image_path)
        
        # ВАЖНО: Всегда конвертируем в RGB для консистентности
        if img.mode != 'RGB':
            img = img.convert('RGB')
            if self.debug:
                print(f"[DEBUG EMBED] Converted image mode from {img.mode} to RGB")
            
        # Получаем массив пикселей
        pixels = np.array(img, dtype=np.uint8)
        height, width = pixels.shape[:2]
        total_pixels = height * width
        
        if self.debug:
            print(f"[DEBUG EMBED] Image size: {width}x{height} = {total_pixels} pixels")
        
        # Подготавливаем данные с заголовком длины
        data_length = len(data)
        header = struct.pack('>I', data_length)  # 4 байта для длины
        full_data = header + data
        
        if self.debug:
            print(f"[DEBUG EMBED] Header bytes: {header.hex()}")
            print(f"[DEBUG EMBED] Full data length: {len(full_data)} bytes")
        
        # Преобразуем в биты
        bits = self._bytes_to_bits(full_data)
        needed_pixels = len(bits)
        
        if self.debug:
            print(f"[DEBUG EMBED] Total bits to embed: {needed_pixels}")
            print(f"[DEBUG EMBED] First 32 bits: {bits[:32]}")
        
        # Генерируем последовательность пикселей
        seed = password.encode() + b'stegoghost'
        pixel_indices = self._generate_pixel_sequence(seed, total_pixels, needed_pixels)
        
        # Внедряем биты
        flat_pixels = pixels.reshape(-1, 3).copy()  # Важно: делаем копию
        
        if self.debug:
            # Проверяем первые несколько пикселей до изменения
            print(f"[DEBUG EMBED] First 5 pixel indices: {pixel_indices[:5]}")
            for i in range(min(5, len(pixel_indices))):
                idx = pixel_indices[i]
                print(f"[DEBUG EMBED] Pixel {idx} before: R={flat_pixels[idx][0]}")
        
        for bit_idx, pixel_idx in enumerate(pixel_indices):
            # Используем красный канал для LSB
            red_value = flat_pixels[pixel_idx][0]
            # Очищаем LSB и устанавливаем новый бит
            new_red = (red_value & 0xFE) | bits[bit_idx]
            flat_pixels[pixel_idx][0] = new_red
            
        if self.debug:
            # Проверяем первые несколько пикселей после изменения
            for i in range(min(5, len(pixel_indices))):
                idx = pixel_indices[i]
                print(f"[DEBUG EMBED] Pixel {idx} after: R={flat_pixels[idx][0]}, embedded bit: {bits[i]}")
            
        # Восстанавливаем форму и создаем новое изображение
        modified_pixels = flat_pixels.reshape(height, width, 3)
        result_img = Image.fromarray(modified_pixels, mode='RGB')
        
        if self.debug:
            print(f"[DEBUG EMBED] Embedding completed successfully")
            print(f"[DEBUG EMBED] Result image mode: {result_img.mode}")
        
        return result_img
    
    def extract_data(self, image_path: str, password: str) -> Optional[bytes]:
        """
        Извлекает данные из изображения
        
        Args:
            image_path: Путь к изображению с данными
            password: Пароль для генерации seed
            
        Returns:
            Извлеченные зашифрованные данные или None
        """
        try:
            if self.debug:
                print(f"\n[DEBUG EXTRACT] Starting extraction...")
                print(f"[DEBUG EXTRACT] Password: {password}")
            
            # Загружаем изображение
            img = Image.open(image_path)
            
            # ВАЖНО: Всегда конвертируем в RGB для консистентности
            if img.mode != 'RGB':
                img = img.convert('RGB')
                if self.debug:
                    print(f"[DEBUG EXTRACT] Converted image mode from {img.mode} to RGB")
                
            pixels = np.array(img, dtype=np.uint8)
            height, width = pixels.shape[:2]
            total_pixels = height * width
            
            if self.debug:
                print(f"[DEBUG EXTRACT] Image size: {width}x{height} = {total_pixels} pixels")
                print(f"[DEBUG EXTRACT] Image mode: {img.mode}")
            
            # Генерируем seed
            seed = password.encode() + b'stegoghost'
            
            # Сначала извлекаем заголовок (4 байта = 32 бита)
            header_bits_count = self.header_size * 8
            
            # ВАЖНО: Получаем индексы для заголовка с offset=0
            header_indices = self._generate_pixel_sequence(seed, total_pixels, header_bits_count, offset=0)
            
            # Извлекаем биты заголовка
            flat_pixels = pixels.reshape(-1, 3)
            header_bits = []
            
            if self.debug:
                print(f"[DEBUG EXTRACT] First 5 header pixel indices: {header_indices[:5]}")
            
            for i, pixel_idx in enumerate(header_indices):
                red_value = flat_pixels[pixel_idx][0]
                bit = red_value & 1
                header_bits.append(bit)
                
                if self.debug and i < 5:
                    print(f"[DEBUG EXTRACT] Pixel {pixel_idx}: R={red_value}, extracted bit: {bit}")
                
            if self.debug:
                print(f"[DEBUG EXTRACT] Header bits: {header_bits}")
                
            # Преобразуем в длину данных
            header_bytes = self._bits_to_bytes(header_bits)
            data_length = struct.unpack('>I', header_bytes)[0]
            
            if self.debug:
                print(f"[DEBUG EXTRACT] Header bytes: {header_bytes.hex()}")
                print(f"[DEBUG EXTRACT] Extracted data length: {data_length}")
            
            # Проверяем разумность длины
            if data_length <= 0 or data_length > self.max_message_length * 10:
                if self.debug:
                    print(f"[DEBUG EXTRACT] Invalid data length: {data_length}")
                return None
                
            # Теперь извлекаем данные с правильным offset
            data_bits_count = data_length * 8
            
            # ВАЖНО: Получаем индексы для данных с offset=header_bits_count
            data_indices = self._generate_pixel_sequence(seed, total_pixels, data_bits_count, offset=header_bits_count)
            
            # Извлекаем биты данных
            data_bits = []
            for pixel_idx in data_indices:
                red_value = flat_pixels[pixel_idx][0]
                bit = red_value & 1
                data_bits.append(bit)
                
            if self.debug:
                print(f"[DEBUG EXTRACT] Extracted {len(data_bits)} data bits")
                if len(data_bits) >= 8:
                    print(f"[DEBUG EXTRACT] First 8 data bits: {data_bits[:8]}")
                
            # Преобразуем биты в байты
            extracted_data = self._bits_to_bytes(data_bits)
            
            # Возвращаем только нужное количество байт
            result = extracted_data[:data_length]
            
            if self.debug:
                print(f"[DEBUG EXTRACT] Successfully extracted {len(result)} bytes")
                
            return result
            
        except Exception as e:
            print(f"[DEBUG EXTRACT] Error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def calculate_capacity(self, image_path: str) -> int:
        """Вычисляет максимальную вместимость изображения в байтах"""
        img = Image.open(image_path)
        width, height = img.size
        total_pixels = width * height
        # Вычитаем заголовок и оставляем запас
        return (total_pixels - self.header_size * 8) // 8 // 2 