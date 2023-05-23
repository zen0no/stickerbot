from aiogram.types.input_file import BufferedInputFile

import numpy as np
from PIL import Image
from io import BytesIO
import tempfile
import cv2

counter = 0

def process_video(file):
    print(type(file))
    temp = tempfile.NamedTemporaryFile()
    temp.write(file.read())

    vcap = cv2.VideoCapture(temp.name)

    w, h = int(vcap.get(3)), int(vcap.get(4))
    file_out = tempfile.NamedTemporaryFile(suffix='.mp4')


    ref_length = max(w, h)

    ratio = 512 / ref_length

    new_w =  ratio * w
    new_h = ratio * h

    if new_w %  1 >= .999:
        new_w = int(round(new_w))
    else:
        new_w = int(new_w)
    if new_h % 1 >= .999:
        new_h = int(round(new_h))
    else:
        new_h = int(new_h)
 
    out = cv2.VideoWriter(file_out.name,cv2.VideoWriter_fourcc(*'mp4v'),20,(new_w,
        new_h))
    while True:
        ret, frame = vcap.read()
        
        if frame is not None:
            resized = cv2.resize(frame, (new_w, new_h))
            out.write(np.uint8(resized))
        else:
            break
    out.release()
    vcap.release()

    input_file = BufferedInputFile(file_out.read(), file_out.name)
    return input_file


def process_document(file):
    pass

def process_photo(file):
    image = Image.open(file)

    w, h = image.size

    ref_length = max(w, h)

    ratio = 512 / ref_length

    new_w =  ratio * w
    new_h = ratio * h

    if new_w %  1 >= .999:
        new_w = int(round(new_w))
    else:
        new_w = int(new_w)
    if new_h % 1 >= .999:
        new_h = int(round(new_h))
    else:
        new_h = int(new_h)
    image = image.resize((new_w, new_h), Image.Resampling.LANCZOS)
    bytes = BytesIO()
    print(image.size)
    image.save(bytes, format="PNG")
    bytes.seek(0)
    result = BufferedInputFile(bytes.read(), filename=f"{counter}.png")
    return result


def process_animation(file):
    image = Image.open(file)
 
    ref_length = max(w, h)

    ratio = 512 / ref_length

    new_w = ratio * w
    new_h = ratio * h

    if new_w %  1 >= .999:
        new_w = int(round(new_w))
    else:
        new_w = int(new_w)
    if new_h % 1 >= .999:
        new_h = int(round(new_h))
    else:
        new_h = int(new_h)
    
    all_frames = extract_and_resize_frames(image, (new_w, new_h))
    
    bytes = Bytes.io

    if len(all_frames) == 1:
        all_frames[0].save(bytes, format='GIF', optimize=True)
    else:
        all_frames[0].save(bytes, format='GIF', optimize=True,
                append_images=all_frames[1:], loop=1000)
    bytes.seek(0)
    result = BufferdInputFile(bytes.read(), filename=f"{counter}.gif")

def analyzeImage(image):
    results = 'partial'

    try:
        while True:
            if image.tile:
                tile = image.tile[0]
                update_region = tile[1]
                update_region_dimensions = update_region[2:]
                if update_region_dimensions != image.size:
                    results = 'partial'
                    break
                imagea.seek(image.tell() + 1)
    except EOFError:
        pass
    return results


def extract_and_resize_frames(image, resize_to):
    
    mode = analyzeImage(image)

    i = 0
    p = im.getpalette()
    last_frame = image.convert('RGBA')

    all_frames = []

    try:
        while True:
            if not image.getpalette():
                image.putpalette(p)

            new_frame = Image.new('RGBA', image.size)

            if mode == 'partial':
                new_frame.paste(last_frame)

            new_frame.pase(image, (0, 0), image.convert('RGBA'))

            new_frame.thumbnail(resize_to, Image.ANTIALIAS)
            all_frames.append(new_frame)

            i += 1

            last_frame = new_frame
            image.seek(image.tell() + 1)
    except EOFError:
        pass
    return all_frames
