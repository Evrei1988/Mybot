import os
import pdfkit
import pytesseract
import cv2
import pandas as pd
from pdf2image import convert_from_path
from PIL import Image
from aiogram import Bot, Dispatcher, types
from aiogram.types import InputFile
from aiogram.utils import executor
from aiogram.types.message import ContentType
from datetime import datetime
import re

# ✅ Указываем путь к Tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ✅ Настройки бота
TOKEN = "8032156423:AAGgjQ_8gcO-PyuDum2sNHBUEh8SlJMb-a4"  # 🔹 Вставь свой токен!
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# ✅ Переменные для хранения фото
user_photos = {}

EXCEL_FILE = "work_orders.xlsx"  # 📂 Файл с таблицами

# ✅ Обработчик команды /start
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    user_photos[message.chat.id] = []  # Очищаем список фото
    await message.reply("Здарова заебал! Отправь 1 скрин с WO, 2 с Notes.")

# ✅ Обработчик фото
@dp.message_handler(content_types=ContentType.PHOTO)
async def handle_photo(message: types.Message):
    user_id = message.chat.id
    if user_id not in user_photos:
        user_photos[user_id] = []

    # 📥 Сохраняем фото
    photo = message.photo[-1]  # Берем фото наивысшего качества
    file = await bot.get_file(photo.file_id)
    file_path = f"{user_id}_{len(user_photos[user_id])}.jpg"
    await bot.download_file(file.file_path, file_path)
    user_photos[user_id].append(file_path)

    if len(user_photos[user_id]) == 2:
        await process_images(message)

async def process_images(message):
    user_id = message.chat.id
    photos = user_photos[user_id]

    # 📝 Распознаем текст
    extracted_data = {}
    for photo in photos:
        img = cv2.imread(photo)
        text = pytesseract.image_to_string(img)

        # 🎯 Извлекаем нужные данные
        extracted_data["name"] = extracted_data.get("name") or extract_field(text, r"TECHNICIAN\s*[-:]\s*([\w\s]+)")
        extracted_data["wo_number"] = extracted_data.get("wo_number") or extract_field(text, r"WO\s*[-: ]?\s*(\d+)")
        extracted_data["sa_number"] = extracted_data.get("sa_number") or extract_field(text, r"SA\s*[-: ]?\s*(\d+)")
        extracted_data["time_start"], extracted_data["time_end"] = extract_time_on_job(text)

    # 📜 Имя PDF-файла = WO-номер
    wo_number = extracted_data.get("wo_number", "Unknown")
    pdf_filename = f"WO-{wo_number}.pdf"

    # 🖼 Создаем PDF из изображений
    images = [Image.open(photo).convert("RGB") for photo in photos]
    images[0].save(pdf_filename, save_all=True, append_images=images[1:])

    # 🕒 Вычисляем общее время работы
    total_time = calculate_total_time(extracted_data["time_start"], extracted_data["time_end"])

    # 📥 Записываем в Excel-файл
    update_excel(wo_number, extracted_data["sa_number"], extracted_data["time_start"], extracted_data["time_end"], total_time)

    # 📤 Отправляем пользователю PDF
    await bot.send_document(user_id, InputFile(pdf_filename), caption="Заебись! Вот твой PDF.")

    # 📤 Отправляем обновленный Excel-файл
    if os.path.exists(EXCEL_FILE):
        await bot.send_document(user_id, InputFile(EXCEL_FILE), caption="Вот обновленная таблица Work Orders.")

    # 🧹 Чистим файлы
    for photo in photos:
        os.remove(photo)
    os.remove(pdf_filename)
    del user_photos[user_id]

# 📝 Функция для извлечения данных с regex
def extract_field(text, pattern):
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1).strip() if match else "Unknown"

def extract_time_on_job(text):
    match = re.search(r"TIME ON JOB\s*[-:]?\s*(\d{1,2}:\d{2}\s*(AM|PM)?)\s*[-–]+\s*(\d{1,2}:\d{2}\s*(AM|PM)?)", text, re.IGNORECASE)
    if match:
        return match.group(1), match.group(3)
    return "Unknown", "Unknown"

# ✅ Функция для обновления Excel-файла
def update_excel(wo_number, sa_number, time_start, time_end, total_time):
    """Обновляет Excel-файл, добавляя данные в соответствующую неделю."""
    
    # 📅 Получаем текущую дату и номер недели
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_week = datetime.now().strftime("%U")  # Номер недели
    sheet_name = f"Week_{current_week}"

    # ✅ Форматируем WO и SA
    wo_number = f"WO-{wo_number}" if wo_number != "Unknown" else "Unknown"
    sa_number = f"SA-{sa_number}" if sa_number != "Unknown" else "Unknown"

    # Данные для добавления
    new_data = {
        "Date": [current_date],  
        "WO": [wo_number],
        "SA": [sa_number],
        "Hrs in": [time_start],
        "Hrs out": [time_end],
        "Total time": [total_time]
    }
    
    new_df = pd.DataFrame(new_data)

    # 📝 Открываем или создаем файл Excel
    try:
        with pd.ExcelWriter(EXCEL_FILE, mode="a", engine="openpyxl", if_sheet_exists="overlay") as writer:
            try:
                df = pd.read_excel(EXCEL_FILE, sheet_name=sheet_name)
            except ValueError:
                df = pd.DataFrame(columns=["Date", "WO", "SA", "Hrs in", "Hrs out", "Total time"])

            # 📝 Удаляем старый Total
            df = df[df["Date"] != "Total"]

            # 📝 Добавляем новые данные
            df = pd.concat([df, new_df], ignore_index=True)

            # 📌 Считаем Total time внизу таблицы
            total_time_sum = sum_total_time(df["Total time"])
            total_row = pd.DataFrame({"Date": ["Total"], "WO": [""], "SA": [""], "Hrs in": [""], "Hrs out": [""], "Total time": [total_time_sum]})
            df = pd.concat([df, total_row], ignore_index=True)

            # 💾 Сохраняем в файл
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            
    
    except FileNotFoundError:
        with pd.ExcelWriter(EXCEL_FILE, mode="w", engine="openpyxl") as writer:
            new_df.to_excel(writer, sheet_name=sheet_name, index=False)

# ✅ Функция для подсчета общего времени
def calculate_total_time(start, end):
    try:
        fmt = "%I:%M%p"
        start_time = datetime.strptime(start, fmt)
        end_time = datetime.strptime(end, fmt)
        delta = end_time - start_time
        return f"{delta.seconds // 3600}h {delta.seconds % 3600 // 60}m"
    except:
        return "Unknown"

# ✅ Функция для суммирования `Total time`
def sum_total_time(total_time_column):
    total_minutes = sum(int(re.search(r"(\d+)h (\d+)m", t).group(1)) * 60 + int(re.search(r"(\d+)h (\d+)m", t).group(2)) for t in total_time_column if "h" in t)
    return f"{total_minutes // 60}h {total_minutes % 60}m"

# 🔥 Запуск бота
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)