from aiogram.types.input_file import InputFile

from Pillow import Image
from io import BytesIO


def process_video(file):
    pass

def process_document(file):
    pass

def process_photo(file):
    image = Image.open(file)

    w, h = image.size

    ref_length = max(w, h)

    ratio = 512 / ref_length

    new_w =  ration * w
    new_h = ratio * h

    if new_w %  1 >= .999:
        new_w = int(round(new_w))
    else:
        new_width = int(new_w)
    if new_height % 1 >= .999:
        new_height = int(round(new_h))
    else:
        new_height = int(new_h)
    image = image.resize(new_w, new_h)
    bytes = BytesIO()
    image.save(bytes, format="WEBP")
    bytes.seek(0)
    
    result = InputFile(bytes)
    return result


