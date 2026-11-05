import asyncio
import io
import os
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
import pandas as pd
import matplotlib.pyplot as plt

# Вставьте сюда токен вашего бота, полученный от @BotFather
TOKEN = "8815976441:AAHAvhPGNYhD4Mjp_5faUN2oh4eWKKroopA"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Создаем папку для временных файлов
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Я бот для визуализации данных.\n"
        "Отправь мне файл **CSV** или **Excel (.xlsx)**, и я построю график по твоим данным!"
    )

@dp.message(F.document)
async def handle_document(message: types.Message):
    document = message.document
    file_name = document.file_name

    # Проверка формата файла
    if not file_name.endswith(('.csv', '.xlsx', '.xls')):
        await message.answer("⚠️ Пожалуйста, отправьте файл в формате CSV или Excel.")
        return

    await message.answer("📥 Скачиваю и обрабатываю файл...")

    # Скачивание файла с привязкой к ID пользователя
    file_info = await bot.get_file(document.file_id)
    ext = os.path.splitext(file_name)[1]
    user_file_path = os.path.join(UPLOAD_DIR, f"{message.from_user.id}{ext}")
    
    await bot.download_file(file_info.file_path, user_file_path)

    try:
        # Чтение данных через pandas
        if ext == '.csv':
            df = pd.read_csv(user_file_path)
        else:
            df = pd.read_excel(user_file_path)

        # Выбираем только числовые колонки для графика
        numeric_df = df.select_dtypes(include=['number'])
        if numeric_df.empty:
            await message.answer("⚠️ В файле нет числовых колонок для построения графика.")
            return

        # Генерация гистограмм
        plt.figure(figsize=(8, 6))
        numeric_df.hist(bins=15, color='teal', edgecolor='black', grid=False)
        plt.suptitle("Гистограмма распределения данных", fontsize=14)
        plt.tight_layout()

        # Сохранение графика в буфер памяти
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=200)
        buf.seek(0)
        plt.close()

        # Отправка готового изображения пользователю
        photo = types.BufferedInputFile(buf.read(), filename="chart.png")
        await message.answer_photo(photo=photo, caption="📊 Вот визуализация ваших данных!")

    except Exception as e:
        await message.answer(f"❌ Ошибка при обработке файла:\n`{e}`", parse_mode="Markdown")

    finally:
        # Удаление временного файла
        if os.path.exists(user_file_path):
            os.remove(user_file_path)

async def main():
    logging.basicConfig(level=logging.INFO)
    print("Бот успешно запущен в VS Code...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())