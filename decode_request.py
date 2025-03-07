import base64

# Твоя строка Base64 (возможно, повреждена или обрезана)
base64_data = "b13ee4ede0e920eeaa67fe5489983fa148d638daaff33b7a8127ae8cfe819985a12f015f05d6217663beb1f7be7f922082263eee78200506cef301aff6a5b939618eef0a55a607aeff7a30b312a6babb1db1cbda41eedd1c9c8026091f0f56"

# Добавляем padding, если его не хватает
missing_padding = len(base64_data) % 4
if missing_padding:
    base64_data += "=" * (4 - missing_padding)

try:
    # Декодируем Base64
    raw_data = base64.b64decode(base64_data, validate=False)

    # Сохраняем в файл для анализа
    with open("decoded_data.bin", "wb") as f:
        f.write(raw_data)

    print("✅ Декодированные данные сохранены в decoded_data.bin")

except Exception as e:
    print(f"❌ Ошибка при декодировании Base64: {e}")
