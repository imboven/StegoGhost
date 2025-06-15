"""
Графический интерфейс StegoGhost
Современный UI с темной темой
"""

import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from stego_engine import StegoEngine
from crypto_module import CryptoModule
import traceback


class StegoGhostGUI(QMainWindow):
    """Главное окно приложения"""
    
    def __init__(self):
        super().__init__()
        self.stego_engine = StegoEngine()
        self.crypto_module = CryptoModule()
        
        self.init_ui()
        self.apply_dark_theme()
        
    def init_ui(self):
        """Инициализация интерфейса"""
        self.setWindowTitle("StegoGhost - Стеганографическое приложение")
        self.setGeometry(100, 100, 800, 600)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Главный layout
        main_layout = QVBoxLayout(central_widget)
        
        # Заголовок
        header = QLabel("🔐 StegoGhost")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("font-size: 24px; font-weight: bold; padding: 10px;")
        main_layout.addWidget(header)
        
        # Табы
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_hide_tab(), "🔒 Скрыть сообщение")
        self.tabs.addTab(self.create_extract_tab(), "🔓 Извлечь сообщение")
        main_layout.addWidget(self.tabs)
        
        # Статус бар
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_status("Готов к работе")
        
    def create_hide_tab(self):
        """Создает вкладку для скрытия сообщений"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Выбор изображения
        image_group = QGroupBox("Изображение")
        image_layout = QHBoxLayout()
        
        self.hide_image_path = QLineEdit()
        self.hide_image_path.setPlaceholderText("Выберите изображение...")
        self.hide_image_path.setReadOnly(True)
        image_layout.addWidget(self.hide_image_path)
        
        browse_btn = QPushButton("Обзор...")
        browse_btn.clicked.connect(self.browse_hide_image)
        image_layout.addWidget(browse_btn)
        
        image_group.setLayout(image_layout)
        layout.addWidget(image_group)
        
        # Сообщение
        message_group = QGroupBox("Сообщение")
        message_layout = QVBoxLayout()
        
        self.message_text = QTextEdit()
        self.message_text.setPlaceholderText("Введите секретное сообщение (до 4096 символов)...")
        message_layout.addWidget(self.message_text)
        
        char_count_layout = QHBoxLayout()
        self.char_count_label = QLabel("Символов: 0 / 4096")
        self.message_text.textChanged.connect(self.update_char_count)
        char_count_layout.addWidget(self.char_count_label)
        char_count_layout.addStretch()
        message_layout.addLayout(char_count_layout)
        
        message_group.setLayout(message_layout)
        layout.addWidget(message_group)
        
        # Пароль
        password_group = QGroupBox("Пароль")
        password_layout = QHBoxLayout()
        
        self.hide_password = QLineEdit()
        self.hide_password.setEchoMode(QLineEdit.Password)
        self.hide_password.setPlaceholderText("Введите надежный пароль...")
        password_layout.addWidget(self.hide_password)
        
        self.show_password_btn = QPushButton("👁")
        self.show_password_btn.setCheckable(True)
        self.show_password_btn.toggled.connect(self.toggle_password_visibility)
        self.show_password_btn.setMaximumWidth(40)
        password_layout.addWidget(self.show_password_btn)
        
        password_group.setLayout(password_layout)
        layout.addWidget(password_group)
        
        # Кнопка скрытия
        self.hide_btn = QPushButton("🔐 Скрыть и сохранить")
        self.hide_btn.clicked.connect(self.hide_message)
        self.hide_btn.setMinimumHeight(40)
        layout.addWidget(self.hide_btn)
        
        # Лог
        self.hide_log = QTextEdit()
        self.hide_log.setReadOnly(True)
        self.hide_log.setMaximumHeight(100)
        layout.addWidget(self.hide_log)
        
        layout.addStretch()
        return widget
        
    def create_extract_tab(self):
        """Создает вкладку для извлечения сообщений"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Выбор изображения
        image_group = QGroupBox("Изображение с сообщением")
        image_layout = QHBoxLayout()
        
        self.extract_image_path = QLineEdit()
        self.extract_image_path.setPlaceholderText("Выберите изображение...")
        self.extract_image_path.setReadOnly(True)
        image_layout.addWidget(self.extract_image_path)
        
        browse_btn = QPushButton("Обзор...")
        browse_btn.clicked.connect(self.browse_extract_image)
        image_layout.addWidget(browse_btn)
        
        image_group.setLayout(image_layout)
        layout.addWidget(image_group)
        
        # Пароль
        password_group = QGroupBox("Пароль")
        password_layout = QHBoxLayout()
        
        self.extract_password = QLineEdit()
        self.extract_password.setEchoMode(QLineEdit.Password)
        self.extract_password.setPlaceholderText("Введите пароль...")
        password_layout.addWidget(self.extract_password)
        
        self.show_extract_password_btn = QPushButton("👁")
        self.show_extract_password_btn.setCheckable(True)
        self.show_extract_password_btn.toggled.connect(self.toggle_extract_password_visibility)
        self.show_extract_password_btn.setMaximumWidth(40)
        password_layout.addWidget(self.show_extract_password_btn)
        
        password_group.setLayout(password_layout)
        layout.addWidget(password_group)
        
        # Кнопка извлечения
        self.extract_btn = QPushButton("🔓 Извлечь сообщение")
        self.extract_btn.clicked.connect(self.extract_message)
        self.extract_btn.setMinimumHeight(40)
        layout.addWidget(self.extract_btn)
        
        # Результат
        result_group = QGroupBox("Извлеченное сообщение")
        result_layout = QVBoxLayout()
        
        self.extracted_text = QTextEdit()
        self.extracted_text.setReadOnly(True)
        result_layout.addWidget(self.extracted_text)
        
        result_group.setLayout(result_layout)
        layout.addWidget(result_group)
        
        layout.addStretch()
        return widget
        
    def apply_dark_theme(self):
        """Применяет темную тему"""
        dark_style = """
        QMainWindow {
            background-color: #1e1e1e;
            color: #ffffff;
        }
        
        QWidget {
            background-color: #1e1e1e;
            color: #ffffff;
        }
        
        QGroupBox {
            border: 1px solid #3a3a3a;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
            font-weight: bold;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }
        
        QLineEdit {
            background-color: #2d2d2d;
            border: 1px solid #3a3a3a;
            border-radius: 3px;
            padding: 5px;
            color: #ffffff;
        }
        
        QTextEdit {
            background-color: #2d2d2d;
            border: 1px solid #3a3a3a;
            border-radius: 3px;
            padding: 5px;
            color: #ffffff;
        }
        
        QPushButton {
            background-color: #0d7377;
            color: white;
            border: none;
            border-radius: 3px;
            padding: 8px;
            font-weight: bold;
        }
        
        QPushButton:hover {
            background-color: #14a085;
        }
        
        QPushButton:pressed {
            background-color: #0a5d61;
        }
        
        QTabWidget::pane {
            border: 1px solid #3a3a3a;
            background-color: #1e1e1e;
        }
        
        QTabBar::tab {
            background-color: #2d2d2d;
            color: #ffffff;
            padding: 8px 20px;
            margin-right: 2px;
        }
        
        QTabBar::tab:selected {
            background-color: #0d7377;
        }
        
        QStatusBar {
            background-color: #2d2d2d;
            color: #ffffff;
        }
        """
        self.setStyleSheet(dark_style)
        
    def browse_hide_image(self):
        """Выбор изображения для скрытия"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Выберите изображение",
            "",
            "Изображения (*.png *.jpg *.jpeg *.webp)"
        )
        if file_path:
            self.hide_image_path.setText(file_path)
            self.update_status(f"Выбрано изображение: {Path(file_path).name}")
            
    def browse_extract_image(self):
        """Выбор изображения для извлечения"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите изображение",
            "",
            "Изображения (*.png *.jpg *.jpeg *.webp)"
        )
        if file_path:
            self.extract_image_path.setText(file_path)
            self.update_status(f"Выбрано изображение: {Path(file_path).name}")
            
    def update_char_count(self):
        """Обновляет счетчик символов"""
        count = len(self.message_text.toPlainText())
        self.char_count_label.setText(f"Символов: {count} / 4096")
        if count > 4096:
            self.char_count_label.setStyleSheet("color: #ff4444;")
        else:
            self.char_count_label.setStyleSheet("color: #44ff44;")
            
    def toggle_password_visibility(self, checked):
        """Переключает видимость пароля"""
        if checked:
            self.hide_password.setEchoMode(QLineEdit.Normal)
            self.show_password_btn.setText("🙈")
        else:
            self.hide_password.setEchoMode(QLineEdit.Password)
            self.show_password_btn.setText("👁")
            
    def toggle_extract_password_visibility(self, checked):
        """Переключает видимость пароля извлечения"""
        if checked:
            self.extract_password.setEchoMode(QLineEdit.Normal)
            self.show_extract_password_btn.setText("🙈")
        else:
            self.extract_password.setEchoMode(QLineEdit.Password)
            self.show_extract_password_btn.setText("👁")
            
    def update_status(self, message):
        """Обновляет статус бар"""
        self.status_bar.showMessage(message)
        
    def hide_message(self):
        """Скрывает сообщение в изображении"""
        try:
            # Проверяем входные данные
            image_path = self.hide_image_path.text()
            message = self.message_text.toPlainText()
            password = self.hide_password.text()
            
            if not image_path:
                QMessageBox.warning(self, "Ошибка", "Выберите изображение")
                return
                
            if not message:
                QMessageBox.warning(self, "Ошибка", "Введите сообщение")
                return
                
            if not password:
                QMessageBox.warning(self, "Ошибка", "Введите пароль")
                return
                
            if len(message) > 4096:
                QMessageBox.warning(self, "Ошибка", "Сообщение слишком длинное")
                return
                
            # Проверяем вместимость
            capacity = self.stego_engine.calculate_capacity(image_path)
            encrypted_size = self.crypto_module.get_encrypted_size(len(message.encode()))
            
            self.hide_log.append(f"📊 Вместимость изображения: {capacity} байт")
            self.hide_log.append(f"📏 Размер зашифрованных данных: {encrypted_size} байт")
            
            if encrypted_size > capacity:
                QMessageBox.warning(
                    self, 
                    "Ошибка", 
                    f"Изображение слишком маленькое. Максимальная вместимость: {capacity} байт"
                )
                return
                
            # Шифруем сообщение
            self.hide_log.append("🔐 Шифрование сообщения...")
            encrypted_data = self.crypto_module.encrypt(message, password)
            self.hide_log.append(f"✅ Зашифровано {len(encrypted_data)} байт")
            
            # Внедряем в изображение
            self.hide_log.append("📝 Внедрение данных в изображение...")
            result_image = self.stego_engine.embed_data(image_path, encrypted_data, password)
            
            # Сохраняем результат
            save_path, _ = QFileDialog.getSaveFileName(
                self,
                "Сохранить изображение",
                "stego_output.png",
                "PNG изображения (*.png)"
            )
            
            if save_path:
                result_image.save(save_path, "PNG")
                self.hide_log.append(f"✅ Успешно сохранено: {Path(save_path).name}")
                self.hide_log.append(f"📊 Внедрено {len(encrypted_data)} байт данных")
                self.update_status("Сообщение успешно скрыто")
                
                # Очищаем поля
                self.message_text.clear()
                self.hide_password.clear()
                
        except Exception as e:
            self.hide_log.append(f"❌ Ошибка: {str(e)}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось скрыть сообщение:\n{str(e)}")
            import traceback
            traceback.print_exc()
            
    def extract_message(self):
        """Извлекает сообщение из изображения"""
        try:
            # Проверяем входные данные
            image_path = self.extract_image_path.text()
            password = self.extract_password.text()
            
            if not image_path:
                QMessageBox.warning(self, "Ошибка", "Выберите изображение")
                return
                
            if not password:
                QMessageBox.warning(self, "Ошибка", "Введите пароль")
                return
                
            # Извлекаем данные
            self.update_status("Извлечение данных...")
            self.extracted_text.append("🔍 Поиск скрытых данных...")
            
            encrypted_data = self.stego_engine.extract_data(image_path, password)
            
            if not encrypted_data:
                self.extracted_text.setText("❌ Сообщение не найдено или неверный пароль")
                self.update_status("Не удалось извлечь сообщение")
                return
                
            self.extracted_text.append(f"✅ Найдено {len(encrypted_data)} байт зашифрованных данных")
            
            # Расшифровываем
            self.update_status("Расшифровка сообщения...")
            self.extracted_text.append("🔓 Расшифровка...")
            
            message = self.crypto_module.decrypt(encrypted_data, password)
            
            if message:
                self.extracted_text.clear()
                self.extracted_text.setText(message)
                self.update_status("Сообщение успешно извлечено")
            else:
                self.extracted_text.setText("❌ Не удалось расшифровать. Проверьте пароль.")
                self.update_status("Ошибка расшифровки")
                
        except Exception as e:
            self.extracted_text.setText(f"❌ Ошибка: {str(e)}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось извлечь сообщение:\n{str(e)}")
            import traceback
            traceback.print_exc()
            
    def closeEvent(self, event):
        """Обработка закрытия приложения"""
        event.accept()


def main():
    """Точка входа в приложение"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Устанавливаем иконку приложения
    app.setWindowIcon(QIcon())
    
    window = StegoGhostGUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main() 