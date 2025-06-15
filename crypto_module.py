"""
Криптографический модуль для StegoGhost
Реализация AES-256-GCM с PBKDF2
"""

import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from typing import Tuple, Optional


class CryptoModule:
    """Модуль для шифрования и расшифровки данных"""
    
    def __init__(self):
        self.salt_size = 32  # 256 бит
        self.nonce_size = 12  # 96 бит для GCM
        self.tag_size = 16   # 128 бит
        self.key_size = 32   # 256 бит
        self.iterations = 100000  # Итерации PBKDF2
        
    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """
        Генерирует ключ из пароля используя PBKDF2
        
        Args:
            password: Пароль пользователя
            salt: Соль для деривации
            
        Returns:
            32-байтный ключ
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.key_size,
            salt=salt,
            iterations=self.iterations,
            backend=default_backend()
        )
        return kdf.derive(password.encode())
    
    def encrypt(self, plaintext: str, password: str) -> bytes:
        """
        Шифрует текст используя AES-256-GCM
        
        Args:
            plaintext: Исходный текст
            password: Пароль для шифрования
            
        Returns:
            Зашифрованные данные в формате: salt + nonce + tag + ciphertext
        """
        # Генерируем случайные salt и nonce
        salt = os.urandom(self.salt_size)
        nonce = os.urandom(self.nonce_size)
        
        # Выводим ключ из пароля
        key = self._derive_key(password, salt)
        
        # Создаем шифр
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(nonce),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        # Шифруем данные
        plaintext_bytes = plaintext.encode('utf-8')
        ciphertext = encryptor.update(plaintext_bytes) + encryptor.finalize()
        
        # Получаем тег аутентификации
        tag = encryptor.tag
        
        # Собираем все вместе
        encrypted_data = salt + nonce + tag + ciphertext
        
        return encrypted_data
    
    def decrypt(self, encrypted_data: bytes, password: str) -> Optional[str]:
        """
        Расшифровывает данные
        
        Args:
            encrypted_data: Зашифрованные данные
            password: Пароль для расшифровки
            
        Returns:
            Расшифрованный текст или None при ошибке
        """
        try:
            # Проверяем минимальную длину
            min_size = self.salt_size + self.nonce_size + self.tag_size
            if len(encrypted_data) < min_size:
                return None
                
            # Извлекаем компоненты
            salt = encrypted_data[:self.salt_size]
            nonce = encrypted_data[self.salt_size:self.salt_size + self.nonce_size]
            tag = encrypted_data[self.salt_size + self.nonce_size:self.salt_size + self.nonce_size + self.tag_size]
            ciphertext = encrypted_data[self.salt_size + self.nonce_size + self.tag_size:]
            
            # Выводим ключ
            key = self._derive_key(password, salt)
            
            # Создаем дешифратор
            cipher = Cipher(
                algorithms.AES(key),
                modes.GCM(nonce, tag),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            
            # Расшифровываем
            plaintext_bytes = decryptor.update(ciphertext) + decryptor.finalize()
            
            # Декодируем в строку
            return plaintext_bytes.decode('utf-8')
            
        except Exception:
            # Любая ошибка означает неверный пароль или поврежденные данные
            return None
    
    def get_encrypted_size(self, plaintext_size: int) -> int:
        """Вычисляет размер зашифрованных данных"""
        return self.salt_size + self.nonce_size + self.tag_size + plaintext_size 