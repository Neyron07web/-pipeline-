import hashlib
import argparse
import os
import cv2
import numpy as np
from PIL import Image
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


# Базовый класс стеганографии (уже был)
class ImageSteganography:
    def __init__(self):
        self.delimiter = "###END###"

    def text_to_binary(self, text: str) -> str:
        binary = ''.join(format(ord(char), '08b') for char in text + self.delimiter)
        return binary

    def binary_to_text(self, binary: str) -> str:
        text = ''
        for i in range(0, len(binary) - 64, 8):
            byte = binary[i:i + 8]
            if len(byte) == 8:
                char = chr(int(byte, 2))
                text += char
                if len(text) > 1000:
                    break
        return text.rstrip(self.delimiter)

    def encode_image(self, image_path: str, message: str, output_path: str = None) -> bool:
        try:
            img = cv2.imread(image_path)
            if img is None:
                return False

            binary_message = self.text_to_binary(message)
            flat_img = img.flatten()

            for i in range(len(binary_message)):
                if i < len(flat_img):
                    flat_img[i] = (flat_img[i] & 0xFE) | int(binary_message[i])

            encoded_img = flat_img.reshape(img.shape).astype(np.uint8)

            if output_path is None:
                output_path = image_path.replace('.', '_encoded.')

            cv2.imwrite(output_path, encoded_img)
            return True
        except:
            return False

    def decode_image(self, image_path: str) -> str:
        try:
            img = cv2.imread(image_path)
            if img is None:
                return ""

            flat_img = img.flatten()
            binary_data = ''.join(str(pixel & 1) for pixel in flat_img)
            return self.binary_to_text(binary_data)
        except:
            return ""

    def analyze_capacity(self, image_path: str) -> dict:
        try:
            img = cv2.imread(image_path)
            if img is None:
                return None
            height, width, channels = img.shape
            return {
                'size': f"{height}x{width}",
                'channels': channels,
                'total_bits': height * width * channels,
                'max_chars': (height * width * channels) // 8
            }
        except:
            return None


# Расширенный класс (уже был)
class AdvancedSteganography(ImageSteganography):
    def __init__(self, password: str = None):
        super().__init__()
        self.password = password

    def _apply_password(self, binary_data: str) -> str:
        if not self.password:
            return binary_data
        password_hash = hashlib.sha256(self.password.encode()).digest()
        binary_list = list(binary_data)
        for i in range(len(binary_list)):
            if binary_list[i] in '01':
                pass_char = password_hash[i % len(password_hash)]
                bit_value = int(binary_list[i])
                encrypted_bit = bit_value ^ (pass_char & 1)
                binary_list[i] = str(encrypted_bit)
        return ''.join(binary_list)


# *** НОВЫЙ КЛАСС SteganoGUI ***
class SteganoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Стеганография в изображениях")
        self.root.geometry("600x500")

        self.stego = AdvancedSteganography()

        # Создаем вкладки
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Вкладка встраивания
        self.encode_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.encode_frame, text='Встраивание')
        self.setup_encode_tab()

        # Вкладка извлечения
        self.decode_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.decode_frame, text='Извлечение')
        self.setup_decode_tab()

        # Вкладка анализа
        self.analyze_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.analyze_frame, text='Анализ')
        self.setup_analyze_tab()

    def setup_encode_tab(self):
        ttk.Label(self.encode_frame, text="Исходное изображение:").pack(pady=5)
        self.encode_path = tk.StringVar()
        ttk.Entry(self.encode_frame, textvariable=self.encode_path, width=50).pack(pady=5)
        ttk.Button(self.encode_frame, text="Обзор...",
                   command=self.browse_encode).pack(pady=5)

        ttk.Label(self.encode_frame, text="Секретное сообщение:").pack(pady=5)
        self.message_text = tk.Text(self.encode_frame, height=5, width=50)
        self.message_text.pack(pady=5)

        ttk.Label(self.encode_frame, text="Пароль (опционально):").pack(pady=5)
        self.password_encode = ttk.Entry(self.encode_frame, show="*")
        self.password_encode.pack(pady=5)

        ttk.Button(self.encode_frame, text="Встроить сообщение",
                   command=self.encode_message).pack(pady=20)

    def setup_decode_tab(self):
        ttk.Label(self.decode_frame, text="Изображение с сообщением:").pack(pady=5)
        self.decode_path = tk.StringVar()
        ttk.Entry(self.decode_frame, textvariable=self.decode_path, width=50).pack(pady=5)
        ttk.Button(self.decode_frame, text="Обзор...",
                   command=self.browse_decode).pack(pady=5)

        ttk.Label(self.decode_frame, text="Пароль:").pack(pady=5)
        self.password_decode = ttk.Entry(self.decode_frame, show="*")
        self.password_decode.pack(pady=5)

        ttk.Button(self.decode_frame, text="Извлечь сообщение",
                   command=self.decode_message).pack(pady=10)

        self.result_text = tk.Text(self.decode_frame, height=5, width=50)
        self.result_text.pack(pady=5)

    def setup_analyze_tab(self):
        ttk.Label(self.analyze_frame, text="Изображение для анализа:").pack(pady=5)
        self.analyze_path = tk.StringVar()
        ttk.Entry(self.analyze_frame, textvariable=self.analyze_path, width=50).pack(pady=5)
        ttk.Button(self.analyze_frame, text="Обзор...",
                   command=self.browse_analyze).pack(pady=5)

        ttk.Button(self.analyze_frame, text="Анализировать",
                   command=self.analyze_image).pack(pady=20)

        self.analyze_result = tk.Text(self.analyze_frame, height=10, width=50)
        self.analyze_result.pack(pady=5)

    def browse_encode(self):
        filename = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")])
        if filename:
            self.encode_path.set(filename)

    def browse_decode(self):
        filename = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")])
        if filename:
            self.decode_path.set(filename)

    def browse_analyze(self):
        filename = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")])
        if filename:
            self.analyze_path.set(filename)

    def encode_message(self):
        image_path = self.encode_path.get()
        message = self.message_text.get("1.0", tk.END).strip()
        password = self.password_encode.get()

        if not image_path or not message:
            messagebox.showerror("Ошибка", "Заполните все поля!")
            return

        output_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                   filetypes=[("PNG files", "*.png")])

        if output_path:
            self.stego.password = password
            success = self.stego.encode_image(image_path, message, output_path)
            if success:
                messagebox.showinfo("Успех", "Сообщение успешно встроено!")
            else:
                messagebox.showerror("Ошибка", "Не удалось встроить сообщение")

    def decode_message(self):
        image_path = self.decode_path.get()
        password = self.password_decode.get()

        if not image_path:
            messagebox.showerror("Ошибка", "Выберите изображение!")
            return

        self.stego.password = password
        message = self.stego.decode_image(image_path)

        self.result_text.delete("1.0", tk.END)
        if message:
            self.result_text.insert("1.0", message)
        else:
            self.result_text.insert("1.0", "Сообщение не найдено")

    def analyze_image(self):
        image_path = self.analyze_path.get()
        if not image_path:
            messagebox.showerror("Ошибка", "Выберите изображение!")
            return

        capacity = self.stego.analyze_capacity(image_path)
        self.analyze_result.delete("1.0", tk.END)

        if capacity:
            result = "Информация об изображении:\n"
            for key, value in capacity.items():
                result += f"  {key}: {value}\n"
            self.analyze_result.insert("1.0", result)
        else:
            self.analyze_result.insert("1.0", "Не удалось проанализировать изображение")


def batch_process():
    """Пакетная обработка"""
    parser = argparse.ArgumentParser(
        description='Стеганография в изображениях',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  python main.py --mode encode --input image.png --message "СЕКРЕТ"
  python main.py --mode decode --input encoded.png  
  python main.py --mode analyze --input image.png
        """
    )

    parser.add_argument('--mode', choices=['encode', 'decode', 'analyze'],
                        required=False, help='Режим работы')
    parser.add_argument('--input', required=False, help='Входное изображение')
    parser.add_argument('--output', help='Выходное изображение')
    parser.add_argument('--message', help='Секретное сообщение')
    parser.add_argument('--password', help='Пароль')

    args = parser.parse_args()

    if not args.mode:
        print("Запуск GUI...")
        create_gui()
        return

    stego = AdvancedSteganography(args.password)

    if args.mode == 'encode' and args.message and args.input:
        success = stego.encode_image(args.input, args.message, args.output)
        print("✅" if success else "❌", "Кодирование завершено")
    elif args.mode == 'decode' and args.input:
        message = stego.decode_image(args.input)
        print(f"Сообщение: {message or 'не найдено'}")
    elif args.mode == 'analyze' and args.input:
        capacity = stego.analyze_capacity(args.input)
        print("Анализ:", capacity or "ошибка")


def create_gui():
    root = tk.Tk()
    app = SteganoGUI(root)
    root.mainloop()


if __name__ == "__main__":
    batch_process()
