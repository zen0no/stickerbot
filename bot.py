from aiogram import Bot, Dispatcher, Router, types
from aiogram.types import reply_keyboard
from aiogram.types.input_sticker import InputSticker
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from state import StickerAdd
from process import *

from emoji import is_emoji 

import logging
import os

logging.basicConfig(level=logging.INFO)


router = Router()

bot = Bot(os.environ.get("BOT_TOKEN"))
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)

finilize_markup = reply_keyboard.ReplyKeyboardMarkup()
finilize_markup.row(*[reply_keyboard.KeyboardButton("Добавить стикер"),
                    reply_keyboard.KeyboardButton("Создать стикерпак")],
                    resize_keyboard=True)


def text_emoji(s):
    for i in s:
        if not is_emoji(i):
            return False
    return True


@dp.message_handler(commands=['start', 'help'])
async def start_info(message: types.Message):
    await bot.send_message(message.chat.id, "HELO")

@dp.message_handler(commands=['newsticker'])
async def newsticker(message: types.Message):
    await bot.send_message(message.chat.id, 
            'Отлично, для начала дайте имя своему стикерпаку')
    await StickerAdd.set_name.set()

# Задаём имя стикерпака
@dp.message_handler(Text(equals="Добавить стикер", ignore_case=True),
        state=StickerAdd.finilize)
@dp.message_handler(state=StickerAdd.set_name)
async def set_sticker_pack_name(message: types.Message, state: FSMContext):  
    async with state.proxy() as data:
        data['title'] = message.text
        data['files'] = []
        data['emoji'] = []
    await bot.send_message(message.chat.id,
            'Отлично, теперь отправьте файл стикера')
    await StickerAdd.file.set()
    

# Добавляем обработчики для файлов

@dp.message_handler(content_types=['photo'], state=StickerAdd.file)
async def handle_video(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        processed_input = process_photo(message.photo)
        data['files'].append(processed_input)
    await bot.send_message(message.chat.id, 'Какой эмодзи выберите для этого стикера?')
    await StickerAdd.emoji.set()


@dp.message_handler(content_types=['video'], state=StickerAdd.file)
async def handle_video(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        file = await bot.get_file(meesage.video.file_id)
        video = await bot.download(message.video)
        processed_input = process_video(message.video)
        data['files'].append(processed_input)
    await bot.send_message(message.chat.id, 'Какой эмодзи выберите для этого стикера?')
    await StickerAdd.emoji.set()

@dp.message_handler(content_types=['document'], state=StickerAdd.file)
async def handle_video(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        processed_input = process_video(message.video)
        data['files'].append(processed_input)
    await bot.send_message(message.chat.id, 'Какой эмодзи выберите для этого стикера?')
    await StickerAdd.emoji.set()



# получаем эмоджи для стикера
@dp.message_handler(lambda message: is_emoji(message.text),
        state=StickerAdd.emoji)
async def set_sticker_emoji(message: types.Message, state=FSMContext):
    async with state.proxy() as data:
        data['emoji'].append(list(message.text))

    await bot.send_message(message.chat.id, 'Окей, я добавил. Я могу добавить ещё стикер, либо же создать стикерпак', reply_markup=finilize_markup)
    await StickerAdd.finilize.set()

@dp.message_handler(Text(equals='Создать стикерпак', ignore_case=True),state=StickerAdd.finilize)
async def create_sticker_pack(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        stickers = [InputSticker(f, s) for f, s in zip(data['files'], data['emoji'])]
        if await bot.createNewStickerSet(message.from_user.id, data['title'], stickers):
            await bot.send_message(message.chat.id, "Что-то пошло не так, попробуйте снова")
        else: 
            await bot.send_message(message.chat.id, "Стикерпак успешно создан")
    state.finish()


@dp.message_handler()
async def trash_handle(message: types.Message):
    await bot.send_message(message.chat.id, "Введие /newsticker для создания стикерпака")


if __name__ == '__main__':
    executor.start_polling(dp)
