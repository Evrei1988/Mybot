import cv2
import pytesseract
import re

# 🔹 Укажи путь к Tesseract (если Windows, укажи свой путь)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_image(image_path):
    """Распознаёт текст с изображения (с улучшенной обработкой)"""
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # Градации серого
    blurred = cv2.GaussianBlur(gray, (5,5), 0)  # Размытие для удаления шумов
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 11, 2)  # Бинаризация
    
    text = pytesseract.image_to_string(thresh)
    return text

def extract_data(text):
    """Извлекает ФИО, WO-номер, SA-номер и время работы"""
    name = re.search(r"TECHNICIAN\s*-\s*([\w\s]+)", text, re.IGNORECASE)
    wo_number = re.search(r"WO-?(\d+)", text, re.IGNORECASE)
    sa_number = re.search(r"SA-?(\d+)", text, re.IGNORECASE)
    time_job = re.search(r"TIME ON JOB\s*-\s*(\d{1,2}:\d{2}\s*(AM|PM)?)-(\d{1,2}:\d{2}\s*(AM|PM)?)", text, re.IGNORECASE)

    return {
        "name": name.group(1) if name else "Unknown",
        "wo_number": wo_number.group(1) if wo_number else "Unknown",
        "sa_number": sa_number.group(1) if sa_number else "Unknown",
        "time_start": time_job.group(1) if time_job else "Unknown",
        "time_end": time_job.group(3) if time_job else "Unknown"
    }

# 🔹 Сначала распознаём текст
text_1 = extract_text_from_image("photo_1.jpg")
text_2 = extract_text_from_image("photo_2.jpg")

print("\n📜 Полный текст с первого фото:\n", text_1)
print("\n📜 Полный текст со второго фото:\n", text_2)

# 🔹 Затем извлекаем данные
data_1 = extract_data(text_1)
data_2 = extract_data(text_2)

print("\n✅ Распознанные данные с первого фото:")
print(data_1)

print("\n✅ Распознанные данные со второго фото:")
print(data_2)

import re

def clean_text(text):
    """Удаляет лишние пробелы, переводы строк и случайные символы"""
    return text.strip().replace("\n", " ") if text else "Unknown"

def clean_name(name):
    """Удаляет случайные цифры в конце имени"""
    name = re.sub(r"\s*\d+$", "", name)  # Убираем цифры в конце
    return name.strip()

def extract_data(text):
    """Извлекает ФИО, WO-номер, SA-номер и время работы (исправлено)"""
    
    name = re.search(r"TECHNICIAN\s*[-:]\s*([\w\s]+)", text, re.IGNORECASE)
    wo_number = re.search(r"WO\s*[-: ]?\s*(\d+)", text, re.IGNORECASE)
    sa_number = re.search(r"SA\s*[-: ]?\s*(\d+)", text, re.IGNORECASE)
    time_job = re.search(r"TIME ON JOB\s*[-:]?\s*(\d{1,2}:\d{2}\s*(AM|PM)?)\s*[-–]+\s*(\d{1,2}:\d{2}\s*(AM|PM)?)", text, re.IGNORECASE)

    return {
        "name": clean_name(clean_text(name.group(1))) if name else "Unknown",  # ✅ Убрали цифру "2" в конце
        "wo_number": clean_text(wo_number.group(1)) if wo_number else "Unknown",
        "sa_number": clean_text(sa_number.group(1)) if sa_number else "Unknown",
        "time_start": clean_text(time_job.group(1)) if time_job else "Unknown",
        "time_end": clean_text(time_job.group(3)) if time_job else "Unknown"
    }

# 🔹 Распознаём данные
data_1 = extract_data(text_1)
data_2 = extract_data(text_2)

# 🔥 Теперь WO и SA берутся из второго фото, если в первом их нет
final_data = {
    "name": data_1["name"] if data_1["name"] != "Unknown" else data_2["name"],
    "wo_number": data_1["wo_number"] if data_1["wo_number"] != "Unknown" else data_2["wo_number"],
    "sa_number": data_1["sa_number"] if data_1["sa_number"] != "Unknown" else data_2["sa_number"],
    "time_start": data_1["time_start"] if data_1["time_start"] != "Unknown" else data_2["time_start"],
    "time_end": data_1["time_end"] if data_1["time_end"] != "Unknown" else data_2["time_end"]
}

print("\n✅ Итоговые данные:")
print(final_data)

import requests
from datetime import datetime

# Твой URL формы (без "/viewform")
GOOGLE_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeOdz1y3pu8WJ9WdXkPoHlDcjRWeyQdSWvmhwoqsKoUFvGSjw/viewform?usp=dialog"

# URL для отправки данных
FORM_RESPONSE_URL = GOOGLE_FORM_URL + "/formResponse"

# Данные, полученные из OCR
data = {
    "name": "Sergei Posysoev",  # Имя (будет проставлена галочка)
    "wo_number": "1794125",     # WO-номер
    "sa_number": "2023550",     # SA-номер
    "time_start": "14:57",      # Время начала (24-часовой формат)
    "time_end": "16:07"         # Время окончания
}

# Дата (автоматически определяем сегодняшнюю)
current_date = datetime.today()
day = current_date.day
month = current_date.strftime("%B")  # Название месяца (Google Forms использует текстовое значение)

# Поля формы
form_data = {
    "entry.1179944082": "true",        # Галочка
    "entry.1663783792_day": day,       # День
    "entry.1663783792_month": month,   # Месяц
    "entry.1507949236": data["sa_number"],  # SA-номер
    "entry.1601721281": data["wo_number"],  # WO-номер
    "entry.834778282_minute": data["time_end"].split(":")[1],  # Минуты (Время окончания)
    "entry.834778282_hour": data["time_end"].split(":")[0],    # Часы (Время окончания)
    "entry.145104768_minute": data["time_start"].split(":")[1],  # Минуты (Время начала)
    "entry.145104768_hour": data["time_start"].split(":")[0]     # Часы (Время начала)
}

# Заголовки (важно, чтобы Google не отклонил запрос)
headers = {
    "Referer": GOOGLE_FORM_URL + "/viewform",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
}

# Отправляем POST-запрос
response = requests.post(FORM_RESPONSE_URL, data=form_data, headers=headers)

# Проверяем статус
if response.status_code == 200:
    print("✅ Форма успешно отправлена!")
else:
    print(f"⚠️ Ошибка: {response.status_code}")

