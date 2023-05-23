
from aiogram.fsm.state import State, StatesGroup

class StickerAdd(StatesGroup):
    set_name = State()
    type = State()
    file = State()
    emoji = State()
    finilize = State()
