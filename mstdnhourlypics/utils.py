def is_image_file(filename: str):
    ext = filename.split(".")[-1].strip().lower()
    return ext in {"jpg", "jpeg", "png", "gif", "webp"}
