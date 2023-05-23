import asyncio
import logging
import sys
import os
from os import getenv

from aiogram import Bot, F, Dispatcher, Router, types
from aiogram.filters import Command
from aiogram.types.input_sticker import InputSticker
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from state import StickerAdd
from process import *

from emoji import is_emoji


bot = Bot(getenv('BOT_TOKEN'))
router = Router()

finilize_markup = types.ReplyKeyboardMarkup(
        keyboard=[[
            types.KeyboardButton(text="Добавить стикер"),
            types.KeyboardButton(text="Создать стикерпак")
        ]],
        resize_keyboard=True
)

types_markup = types.ReplyKeyboardMarkup(
        keyboard=[[
            types.KeyboardButton(text='Видео'),
            types.KeyboardButton(text='Картинка')
        ]],
        resize_keyboard=True
    )

def text_emoji(s):
    for c in s:
        if not is_emoji(c):
            return False
    return True



@router.message(Command(commands=['start']))
async def start_help(message: types.Message) -> None:
    await message.answer("Добро пожаловать! Этот бот может сделать стикерпак, просто введите команду /newsticker")

@router.message(Command(commands=['newsticker']))
async def newsticker(message: types.Message, state: FSMContext):
    await message.answer('Отлично, для начала дайте имя своему стикерпаку',
            markup=types.ReplyKeyboardRemove())
    await state.set_state(StickerAdd.set_name)

@router.message(StickerAdd.set_name, F.text)
async def set_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text, files=[], emoji=[])
    await state.set_state(StickerAdd.type)
    await message.answer("Выберите тип картинки",
            reply_markup=types_markup)

@router.message(StickerAdd.type, F.text)
async def select_type(message: types.Message, state: FSMContext): 
    t = str()
    if F.text.lower() == "видео":
        t = 'video'
    elif F.text.lower() == "картинка":
        t = 'static'
    else:
        await message.answer('Нет такого типа')
        return
    await state.update_data(type_=t)
    await state.set_state(StickerAdd.file)
    await message.answer("Отправьте файл для стикера",
            reply_markup=types.ReplyKeyboardRemove())

@router.message(StickerAdd.file, F.content_type == 'photo')
async def handle_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if data['type_'] != 'static':
        await message.answer("Неизвестный формат сообщения")
        return
    file = await bot.download(message.photo[0])
    file.seek(0)
    processed_input = process_photo(file)
    data['files'].append(processed_input)
    await state.set_state(StickerAdd.emoji)
    await message.answer("Какой эмодзи для этого стикера нужен?")


@router.message(StickerAdd.file, F.content_type == 'video')
async def handle_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    
    if data['type_'] != 'video':
        await message.answer("Неизвестный формат сообщения")
        return

    file = await bot.get_file(message.video.file_id)
    video = await bot.download(file)
    processed_input = process_video(video)
    data['files'].append(processed_input)
    await state.set_state(StickerAdd.emoji)
    await message.answer("Какой эмодзи для этого стикера нужен?")


@router.message(StickerAdd.file, F.content_type == 'document')
async def handle_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    print(message.document.mime_type)
    file = await bot.get_file(message.document.file_id)
    document = await bot.download(file)
    #processed_input = process_photo(document)
    #data['files'].append(processed_input)
    #await state.set_state(StickerAdd.emoji)
    #await message.answer("Какой эмодзи для этого стикера нужен?")
    

@router.message(StickerAdd.file, F.content_type == 'animation')
async def handle_animation(message: types.Message, state: FSMContext):
    data = await state.get_data()
    file = await bot.get_file(message.animation.file_id)
    print(message.animation.mime_type)
    animation = await bot.download(file)

    processd_input = process_animation(animation)
    adata['files'].append(processed_input)
    await state.set_state(StickerAdd.emoji)
    await message.answer("Какой эмодзи нужен для стикера")

@router.message(StickerAdd.file)
async def handle_other_files(message: types.Message, state: FSMContext):
    await message.answer("Неизвестный формат сообщения")

@router.message(StickerAdd.emoji, lambda message: text_emoji(message.text))
async def select_emoji(message: types.Message, state: FSMContext):
    data = await state.get_data()
    data['emoji'].append(list(message.text))

    await message.answer('Хотите добавить ещё стикер?',
            reply_markup=finilize_markup)
    await state.set_state(StickerAdd.finilize)

@router.message(StickerAdd.finilize, F.text.lower() == 'создать стикерпак')
async def create_stickerpack(message: types.Message, state: FSMContext):
    data = await state.get_data()
    name = f'stickers_{data["title"]}_by_file_to_sticker_bot'
    stickers = [InputSticker(sticker=f, emoji_list=s) for f, s in zip(data['files'], data['emoji'])]
    if await bot.create_new_sticker_set(
            user_id=message.from_user.id,
            name=name, 
            title=data['title'],
            stickers=stickers,
            sticker_format=data['type_']):
        await message.answer(f'Стикерпак успешно создан. Вот ссылка на него: t.me/addstickers/{name}',
                reply_markup=types.ReplyKeyboardRemove())
    else:
        await message.answer('Что-то пошло не так, попробуйте снова',
                reply_markup=types.ReplyKeyboardRemove())

    await state.clear()


@router.message(StickerAdd.finilize, F.text.lower() == 'добавить стикер')
async def add_one_more(message: types.Message, state: FSMContext):
    await state.set_state(StickerAdd.file)
    await message.answer("Отправьте файл стикера")


async def main():
 
    logging.basicConfig(level=logging.INFO)


    storage = MemoryStorage()
    dp = Dispatcher(bot=bot, storage=storage) 
    dp.include_router(router)

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
