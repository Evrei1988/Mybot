import os

EXCEL_FILE = "work_orders.xlsx"

if os.path.exists(EXCEL_FILE):
    os.remove(EXCEL_FILE)
    print("✅ Файл work_orders.xlsx удален. Новый файл создастся при следующем запуске бота.")
else:
    print("⚠️ Файл не найден.")