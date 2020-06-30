from PIL import Image

def scale_image_too_big(image_path):
    image = Image.open(image_path)
    w, h = image.size
    
    if w <= 512 and h <= 512:
        return
    
    if w > h:
        h = int(h * 512 / w)
        w = 512
    else:
        w = int(w * 512 / h)
        h = 512

    image = image.resize((w,h))
    image.save(image_path)
    
