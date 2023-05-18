
from aiogram.dispatcher.filters.state import State, StatesGroup

class StickerAdd(StatesGroup):
    set_name = State()
    file = State()
    emoji = State()
    finilize = State()
